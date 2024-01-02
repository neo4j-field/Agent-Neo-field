from typing import Optional, Callable, Dict, Any
from typing import List, Tuple
from itertools import chain
import pandas as pd
from langchain.document_loaders import UnstructuredURLLoader
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter, TokenTextSplitter
from google.cloud import storage
from google.oauth2 import service_account
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import json
import os
import io
import time
import requests


class Fetcher:
    def __init__(self, client: storage.Client = None):
        self.client = client or storage.Client()
        self.service_account = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')

    def get_sitemap_urls(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_SITEMAPS_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_practitioner_guide_md(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_PRACTITIONERS_GUIDE_SITES_BUCKET')
        return self._read_from_gcp(bucket_name)

    def get_other_articles(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        if bucket_name is None:
            bucket_name = os.environ.get('GCP_OTHER_ARTICLES_BUCKET')
        return self._read_from_gcp(bucket_name)
    
    def _get_youtube_video_info(self, bucket_name: str = None) -> pd.DataFrame:
        if bucket_name is None:
            raise ValueError("Bucket name must be provided.")
        bucket = self.client.get_bucket(bucket_name)
        videos_temp = bucket.get_blob("youtube/neo4j_video_info.csv")
        videos_temp = videos_temp.download_as_string()
        videos = pd.read_csv(io.BytesIO(videos_temp))[['id', 'title']]
        return videos

    def _read_from_gcp(self, bucket_name: str, blob_name: str = None) -> Dict[str, Any]:

        bucket = self.client.get_bucket(bucket_name)

        if not blob_name:
            blobs = list(bucket.list_blobs())
            if not blobs:
                return []
            blob_name = blobs[0].name

        blob = bucket.get_blob(blob_name)

        if blob is None:
            return []

        content = blob.download_as_text()
        data = json.loads(content)
        return data

    @staticmethod
    def concatenate_unique_ordered(*lists: List) -> List:
        seen = set()
        result = []
        for item in chain(*lists):
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result


class WebContentChunker:

    def __init__(self, client: storage.Client = None) -> None:
        if not client:
            credentials = service_account.Credentials.from_service_account_file(
                    os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
                )  
            self.client = storage.Client(credentials=credentials)
        else:
            self.client = client

        self.service_account = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
        self.bucket_name = "agent-neo-neo4j-cs-team-201901-docs"
        self.bucket = self.client.get_bucket(self.bucket_name)
        self._chunked_documents = []

    @property
    def chunk_texts(self) -> List[str]:
        self._assert_documents_chunked()
        return [chunk.page_content for chunk in self._chunked_documents]

    @property
    def chunk_urls(self) -> List[str]:
        self._assert_documents_chunked()
        return list({chunk.metadata.get('source', '') for chunk in self._chunked_documents})

    @property
    def chunks_as_dict(self) -> Dict[str, List[str]]:
        self._assert_documents_chunked()

        result = {}
        for k in self.chunk_urls:
            result.update({k: []})
        
        else:
            for chunk in self._chunked_documents:
                result.get(chunk.metadata.get('source')).append(chunk.page_content)

        return result
    
    @property
    def youtube_chunks_as_dict(self) -> Dict[str, Dict[str, str]]:

        result = {}
        for k in self.chunk_urls:
            result.update({k: []})

        for chunk in self._chunked_documents:
            result.get(chunk.metadata.get('source')).append({
                                                            "video_id": chunk.metadata.get("video_id"),
                                                            "title": chunk.metadata.get("title"),
                                                            "publish_date": chunk.metadata.get("publish_date"),
                                                            "transcript": chunk.page_content
                                                            })
        
        return result
    
    @property
    def youtube_chunks_as_list(self) -> List[Dict[str, str]]:

        result = []

        for chunk in self._chunked_documents:
            result+=[{
                    "url": "https://www.youtube.com/watch?v="+chunk.metadata.get("video_id"),
                    "video_id": chunk.metadata.get("video_id"),
                    "title": chunk.metadata.get("title"),
                    "publish_date": chunk.metadata.get("publish_date"),
                    "transcript": chunk.page_content
                    }]
        
        return result

    def _assert_documents_chunked(self):
        if not self._chunked_documents:
            raise ValueError("Documents have not been chunked yet. Call chunk_documents() first.")

    def _scrape_sites_into_langchain_docs(self, resources: List[str]) -> List[Document]:
        try:
            loader = UnstructuredURLLoader(urls=resources)
            return loader.load()
        except Exception as e:
            print(f"Error loading documents from URLs: {e}")
            return []
    
    @staticmethod
    def _process_youtube_id(id, playlist_title: str) -> str:
        """
        This method strips the address and file suffix from a retrieved id in the 
        transcript loading process.
        """

        if playlist_title != "":
            playlist_title+="/"
        
        result = id.replace("youtube/transcripts/"+playlist_title, "")
        return result.replace(".json", "")
    
    def _get_transcript_text(self, id: str) -> str:
        """
        This method gets the transcript text from the GCP storage bucket address.
        """

        transcript = self.bucket.get_blob("youtube/transcripts/"+id+".txt").download_as_text()
        
        return transcript
    
    def _get_youtube_video_info(self, id: str, playlist_title: str = "") -> Dict[str, str]:

        if playlist_title != "":
            playlist_title+="/"
        # print("youtube/transcripts/"+playlist_title+id+".json")
        info = json.loads(self.bucket.get_blob("youtube/transcripts/"+playlist_title+id+".json").download_as_text())
        
        return info

    def _scrape_youtube_transcripts_into_langchain_docs(self, id_list: List[str] = None, playlist_title: str = "") -> Tuple[List[Document], List[str]]:
        """
        This method retrieves all YouTube transcripts listed in the provided file list from GCP Storage.
        It then formats them into LangChain Documents. 
        """

        docs = []
        unsuccessful = []

        # grab all trancript file addresses in bucket and format to get ids
        if not id_list:
            id_list = [self._process_youtube_id(blob.name, playlist_title) for blob in self.client.list_blobs(self.bucket_name, prefix="youtube/transcripts/"+playlist_title)]

        # grab the transcripts and format into LangChain docs
        for id in id_list:
            try:
                info = self._get_youtube_video_info(id, playlist_title=playlist_title)
                url = "https://www.youtube.com/watch?v="+id
                docs.append(Document(page_content=info['transcript'], metadata={"video_id": id,
                                                                                "source": url, 
                                                                                "publish_date": info['publish_date'],
                                                                                "title": info['title']}))
            except Exception as e:
                print(f"Error loading document with id: {id}")
                print(f"Error: {e}")
                unsuccessful.append(id)

        return docs, unsuccessful

    def _split_into_chunks(self, documents: List[Document],
                           splitter: Callable[[List[Document]], List[Document]]) -> List[Document]:
        return splitter.split_documents(documents)

    def _clean_chunked_documents(self, chunked_docs: List[Document], cleaning_functions: List[Callable[[str], str]]) -> \
            List[Document]:
        for i, doc in enumerate(chunked_docs):
            for func in cleaning_functions:
                doc.page_content = func(doc.page_content)
            chunked_docs[i] = doc
        return chunked_docs

    def chunk_documents(self, urls: List[str],
                        splitter: Callable[[List[Document]], List[Document]] = None,
                        cleaning_functions: List[Callable[[str], str]] = None) -> None:

        if splitter is None:
            splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=1024,
                chunk_overlap=128)

        # Start scraping
        documents = self._scrape_sites_into_langchain_docs(urls)

        # Start splitting
        chunked_docs = self._split_into_chunks(documents, splitter)

        if cleaning_functions:
            chunked_docs = self._clean_chunked_documents(chunked_docs, cleaning_functions)

        self._chunked_documents.extend(chunked_docs)
    
    def chunk_youtube_transcripts(self, 
                                  ids: List[str] = None,
                                  playlist_title: str = "",
                                  splitter: Callable[[List[Document]], List[Document]] = None,
                                  cleaning_functions: List[Callable[[str], str]] = None) -> None:

        if splitter is None:
            splitter = TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=64)

        # Start scraping
        documents, failed = self._scrape_youtube_transcripts_into_langchain_docs(ids, playlist_title=playlist_title)

        # Start splitting
        chunked_docs = self._split_into_chunks(documents, splitter)

        if cleaning_functions:
            chunked_docs = self._clean_chunked_documents(chunked_docs, cleaning_functions)

        self._chunked_documents.extend(chunked_docs)
        
    def __str__(self) -> str:
        return "\n".join([f"Document: {doc}" for doc in self._chunked_documents])
    

    # def list_blobs(self, playlist: str = None) -> List[str]:
    #     """Lists all the blobs in the bucket."""
    #     # bucket_name = "your-bucket-name"

    #     # storage_client = storage.Client()

    #     # Note: Client.list_blobs requires at least package version 1.17.0.
    #     blobs = self.client.list_blobs(self.bucket_name, prefix="youtube/transcripts/"+playlist)

    #     # Note: The call returns a response only when the iterator is consumed.
    #     result = []
    #     for blob in blobs:
    #         # print(blob.name)
    #         result+=[blob.name]
        
    #     return result


    
class GCPStorageLoader:
    """
    This class provides methods for loading new data into the Agent Neo storage buckets.
    """

    def __init__(self, client: storage.Client = None) -> None:
        if not client:
            credentials = service_account.Credentials.from_service_account_file(
                    os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
                )  
            self.client = storage.Client(credentials=credentials)
        else:
            self.client = client

        self.service_account = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
        self.bucket_name = "agent-neo-neo4j-cs-team-201901-docs"
        self.bucket = self.client.get_bucket(self.bucket_name)

        # track failed transcript creations
        # This can happen with unaired live videos
        self._unsuccessful_list = None

        self._recent_youtube_ids = None
    
        self._channel_id = "UCvze3hU6OZBkB1vkhH2lH9Q"
        self._playlist_id = "UUvze3hU6OZBkB1vkhH2lH9Q" # default to the uploads playlist

        self._scraped_video_info = None

    @property
    def channel_id(self) -> str:
        return self._channel_id
    
    @channel_id.setter
    def channel_id(self, channel_id: str) -> None:
        self._channel_id = channel_id
    
    @property
    def playlist_id(self) -> str:
        return self._playlist_id
    
    @playlist_id.setter
    def playlist_id(self, playlist_id: str) -> None:
        self._playlist_id = playlist_id

    def add_new_youtube_urls(self) -> None:
        """
        This method checks for new youtube videos and updates the csv file in GCP Storage.
        """

        pass

    def _get_youtube_video_info(self, video_info_file_name: str) -> pd.DataFrame:

        # if bucket_name is None:
        #     raise ValueError("Bucket name must be provided.")
        # bucket = self.client.get_bucket(bucket_name)
        videos_temp = self.bucket.get_blob("youtube/"+video_info_file_name+".csv")
        videos_temp = videos_temp.download_as_string()
        videos = pd.read_csv(io.BytesIO(videos_temp))[['id', 'title', 'publish_date']]
        return videos
    
    @staticmethod
    def _create_transcript(video_id: str) -> str:
        """
        This method retrieves the video transcript and formats it.
        Returns a string representation of the video transcript.
        """

        raw_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # instantiate the text formatter
        formatter = TextFormatter()

        # format the video into a string without timestamps, etc...
        transcript_formatted = formatter.format_transcript(raw_transcript)

        # replace newlines with a space 

        return transcript_formatted.replace("\n", " ")
    
    def _upload_transcript(self, transcript: str, video_id: str, title: str, publish_date: str, folder: str = "") -> None:
        """
        This method uploads a transcript to GCP Storage.
        Uploading a file will automatically overwrite any existing file with the same id in storage.
        """

        if folder != "":
            folder += "/"

        file_loc = "youtube/transcripts/"+folder
        to_upload = {"video_id": video_id,
                     "title": title,
                     "publish_date": publish_date,
                     "transcript": transcript}
        self.bucket.blob(file_loc+video_id+".json").upload_from_string(json.dumps(to_upload), content_type='application/json')


    def create_and_upload_neo4j_transcripts(self, transcripts_folder: str = "", video_info_file_name: str = "neo4j_video_info") -> List[str]:
        """
        This method:
        1. gets the list of all neo4j video urls from GCP Storage.
        2. gets a transcript of each video. If unsuccessful, is added to list to be returned.
        3. uploads the transcript to GCP Storage.

        returns:
            None
        """

        unsuccessful = []

        videos = self._get_youtube_video_info(video_info_file_name=video_info_file_name)

        total = len(videos)

        for idx, info in videos.iterrows():
            id = info['id']
            try:
                transcript = self._create_transcript(video_id=id)
                self._upload_transcript(transcript=transcript, 
                                        video_id=id, title=info['title'], 
                                        publish_date=info['publish_date'],
                                        folder=transcripts_folder)

            except Exception as e:
                print("Failed: "+id)
                # print(e)
                unsuccessful+=[{"id": id,
                                "title": info['title'],
                                "publish_date": info['publish_date']}]
            
            if idx % 2 == 0:
                print("Progress : ", round((idx+1) / total * 100, 2), "%")
                print("Failed   : ", len(unsuccessful))

            # for demoing
            # if idx >= 10:
            #     break

        self._unsuccessful_list = unsuccessful 

    def update_unsuccessful_transcripts(self, file_name: str = "failed_video_info") -> None:
        """
        This method takes a list of unsuccessful YouTube ids and creates a new csv file
        in GCP Storage for later retrieval. 
        """

        file_loc = "youtube/"

        # create failed df
        failed_df = pd.DataFrame.from_dict(self._unsuccessful_list)

        # check if failed df in GCP storage
        if storage.Blob(bucket=self.bucket, name=file_loc+file_name+".csv").exists(self.client):
            # pull failed df from storage
            videos_temp = self.bucket.get_blob(file_loc+file_name+".csv")
            videos_temp = videos_temp.download_as_string()

            previous_failed_df =  pd.read_csv(io.BytesIO(videos_temp))[['id', 'title']]

            # append new failed df
            new_failed_df = pd.concat(previous_failed_df, failed_df)
            
        else:
            # create first failed df
            new_failed_df = failed_df

        # upload new df to storage
        self.bucket.blob(file_loc+"failed_video_info.csv").upload_from_string(new_failed_df.to_csv(), 'text/csv')

    @staticmethod
    def _get_channel_id() -> str:
        """
        This method retrieves the channel id for the "Neo4j" YouTube channel.
        """

        address = f"https://www.googleapis.com/youtube/v3/search?q=neo4j&key={os.environ.get('YOUTUBE_API_KEY')}&part=snippet"
        req = requests.get(address)
        data = req.json()

        return data['items'][0]['snippet']['channelId']
    
    def _get_playlist_id(self) -> str:
        """
        This method retrieves the uploads id for the channel of interest.
        """

        address = f"https://www.googleapis.com/youtube/v3/channels?id={self._channel_id}&key={os.environ.get('YOUTUBE_API_KEY')}&part=contentDetails"
        try:
            req = requests.get(address)
            data = req.json()
        except ValueError as e:
            print(e, "Provide accurate channel id.")

        return data['items'][0]['contentDetails']['relatedPlaylists']['uploads']


    def scrape_video_info(self, next_page_token: str = None, total_results: int = -1, videos: List[str] = []) -> List[str]:
            
        address = f"https://www.googleapis.com/youtube/v3/playlistItems?playlistId={self.playlist_id}&key={os.environ.get('YOUTUBE_API_KEY')}&part=snippet&maxResults=50"
        
        if not next_page_token:
            vid_req = requests.get(address)

        else:
            vid_req = requests.get(address+f'&pageToken={next_page_token}')
            
        vids = vid_req.json()

        if total_results == -1:
            total_results = vids['pageInfo']['totalResults']
            print('total results set: ', total_results)

        videos += [{"id": x['snippet']['resourceId']['videoId'], 
                    "title": x['snippet']['title'],
                    "publish_date": x['snippet']['publishedAt'][:10]} for x in vids['items']]

        print("total results: ", total_results)
        print("ids retrieved: ", len(videos), "\n")

        if "nextPageToken" not in vids.keys():
            print("complete")
            self._scraped_video_info = videos
            return videos
        
        self.scrape_video_info(next_page_token=vids['nextPageToken'], total_results=total_results, videos=videos)

    def upload_scraped_video_info(self, file_name: str = "neo4j_video_info") -> None:
        """
        This method uploads the scraped video ids to a new csv in the designated GCP Storage bucket.
        """

        file_loc = "youtube/"

        data = pd.DataFrame.from_dict(self._scraped_video_info)

        self.bucket.blob(file_loc+file_name+".csv").upload_from_string(data.to_csv(), 'text/csv')

