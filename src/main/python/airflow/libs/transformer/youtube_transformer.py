from typing import List,Dict, Callable, Tuple, Optional, Any

from google.cloud import storage
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.docstore.document import Document
from langchain.text_splitter import TokenTextSplitter, CharacterTextSplitter
import regex as re

from ..fetcher.secret_manager import SecretManager


class YouTubeTransformer:

    def __init__(self, storage_client: storage.Client = None, secret_client: SecretManager = None) -> None:
        super().__init__(storage_client, secret_client)
        self._storage_client = storage_client or storage.Client()
        self._secret_client = secret_client or SecretManager()

    @property
    def chunk_texts(self) -> List[str]:
        self._assert_documents_chunked()
        return [chunk.page_content for chunk in self._chunked_documents]

    @property
    def chunk_urls(self) -> List[str]:
        self._assert_documents_chunked()
        return list({chunk.metadata.get('source', '') for chunk in self._chunked_documents})

    @property
    def chunk_as_dict(self) -> Dict[str, List[str]]:
        self._assert_documents_chunked()

        result = {}
        for k in self.chunk_urls:
            result.update({k: []})

        for chunk in self._chunked_documents:
            result.get(chunk.metadata.get('source')).append(chunk.page_content)

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
    def _process_youtube_id(id:str) -> str:
        result = id.replace("transcripts/", "")
        return result.replace(".txt", "")

    def _get_transcript_text(self, id: str,bucket_name:str  = None,blob_name: str = None) -> str:
        if bucket_name is None:
            bucket_name = self._secret_client.access_secret_version("bucket_name")

        bucket = self._storage._storage_client.get_bucket(bucket_name)

        if blob_name is None:
            blobs = list(bucket.list_blobs())
            if not blobs:
                raise Exception("No blobs found in the bucket.")
            blob = blobs[0]
        else:

            blob = bucket.blob(blob_name)


        data = blob.download_as_string()

        return data


    def _scrape_youtube_transcripts_into_langchain_docs(self, id_list: List[str] = None) -> Tuple[
        List[Document], List[str]]:


        docs = []
        unsuccessful = []

        # grab all transcript file addresses in bucket and format to get ids
        if not id_list:
            id_list = [self._process_youtube_id(blob.name) for blob in
                       self._storage_client.list_blobs(self.bucket_name, prefix="transcripts/")][1:]

        # grab the transcripts and format into LangChain docs
        for id in id_list:
            try:
                transcript = self._get_transcript_text(id)
                url = "https://www.youtube.com/watch?v=" + id
                docs.append(Document(page_content=transcript, metadata={"source": url}))
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

    def chunk_youtube_transcripts(self, ids: List[str] = None,
                                  splitter: Callable[[List[Document]], List[Document]] = None) -> None:

        if splitter is None:
            splitter = TokenTextSplitter(
                chunk_size=512,
                chunk_overlap=64)

        # Start scraping
        documents, failed = self._scrape_youtube_transcripts_into_langchain_docs(ids)

        # Start splitting
        chunked_docs = self._split_into_chunks(documents, splitter)

        
        chunked_docs = self._clean_chunked_documents(chunked_docs, [self._fix_neo4j_spelling, self._remove_filler_words])

        self._chunked_documents.extend(chunked_docs)

    @staticmethod
    def _remove_filler_words(text: str) -> str:
        """
        This method removes filler words such as "um" or "ah" from a given text.
        """

        filler_words = ["um", "ah", "uh"]

        for word in filler_words:
            text = text.replace(word, "")

        # remove extra whitespace
        return text.strip()

    @staticmethod
    def _fix_neo4j_spelling(text: str) -> str:
        """
        This method corrects the spelling of neo4j in transcripts which is *always* wrong.
        """

        # safe_words = ['freon', 'fern', 'roof']
        return re.sub(r"\b([neoforja ]{4,8})\b", "Neo4j", text, flags=re.IGNORECASE)

    def __str__(self) -> str:
        return "\n".join([f"Document: {doc}" for doc in self._chunked_documents])