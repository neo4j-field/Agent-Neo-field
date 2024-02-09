import io
from typing import List,Dict, Callable, Tuple, Optional, Any

from google.cloud import storage
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from .base_fetcher import BaseFetcher
from .secret_manager import SecretManager


class YoutubeFetcher(BaseFetcher):
    """
    This class provides methods for loading new data into the Agent Neo storage buckets.
    """

    # def __init__(self, client: storage.Client = None) -> None:
    #     if not client:
    #         credentials = service_account.Credentials.from_service_account_file(
    #             os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
    #         )
    #         self.client = storage.Client(credentials=credentials)
    #     else:
    #         self.client = client

    #     self.service_account = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')
    #     self.bucket_name = "agent-neo-neo4j-cs-team-201901-docs"
    #     self.bucket = self._storage_client.get_bucket(self.bucket_name)

    #     # track failed transcript creations
    #     # This can happen with unaired live videos
    #     self._unsuccessful_list = None

    def __init__(self, storage_client: Optional[storage.Client] = None, secret_client: SecretManager = None):
        super().__init__()
        self._storage_client = storage_client or storage.Client()
        self._secret_client = secret_client or SecretManager()
        # secret_data = self._secret_client.access_secret_version('GITHUB_ACCESS_TOKEN')
        self.bucket_name = "agent-neo-youtube"
        self.bucket = self._storage_client.get_bucket(self.bucket_name)

        # track failed transcript creations
        # This can happen with unaired live videos
        self._unsuccessful_list = None

    @property
    def storage_client(self):
        return self._storage_client

    @property
    def secret_manager_client(self):
        return self._secret_manager_client

    def fetch_config(self, secret_name):
        return self._secret_client.access_secret_version(secret_name)

    def fetch(self, *args, **kwargs) -> Any:
        pass

    def add_new_youtube_urls(self) -> None:
        """
        This method checks for new youtube videos and updates the csv file in GCP Storage.
        """

        pass

    def _get_youtube_video_ids(self) -> List[str]:
        """
        This method gets the YouTube video ids csv file from GCP Storage and
        returns a list of the video urls it contains.
        """
        # bucket = self._storage_client.get_bucket(self.bucket_name)

        videos_temp = self.bucket.get_blob("neo4j_video_list.csv")
        videos_temp = videos_temp.download_as_string()
        videos_list = pd.read_csv(io.BytesIO(videos_temp))['YouTube_Address'].to_list()

        return videos_list

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
        transcript_formatted = formatter.format_transcript('')

        # replace newlines with a space

        return transcript_formatted.replace("\n", " ")

    def _upload_transcript(self, transcript: str, video_id: str) -> None:
        """
        This method uploads a transcript to GCP Storage.
        Uploading a file will automatically overwrite any existing file with the same id in storage.
        """

        file_loc = "transcripts/"
        self.bucket.blob(file_loc + video_id + ".txt").upload_from_string(transcript, 'text/plain')

    def create_and_upload_neo4j_transcripts(self) -> List[str]:
        """
        This method:
        1. gets the list of all neo4j video urls from GCP Storage.
        2. gets a transcript of each video. If unsuccessful, is added to list to be returned.
        3. uploads the transcript to GCP Storage.

        returns:
            unsuccessful: list of video ids that were unable to be transcribed.
        """

        unsuccessful = []

        ids = self._get_youtube_video_ids()
        for id in ids:
            try:
                transcript = self._create_transcript(video_id=id)
                self._upload_transcript(transcript=transcript, video_id=id)
                print("Video " + id + " Uploaded to GCP Storage.")
            except Exception as e:
                print("Failed: " + id)
                # print(e)
                unsuccessful += [id]

        return unsuccessful

    def update_unsuccessful_transcripts(self, unsuccessful_list: List[str]) -> None:
        """
        This method takes a list of unsuccessful YouTube ids and creates a new csv file
        in GCP Storage for later retrieval.
        """

        file_loc = ""
        failed_df = pd.Series({"YouTube_Address": unsuccessful_list})
        self.bucket.blob(file_loc + "neo4j_failed_video_list.csv").upload_from_string(failed_df.to_csv(), 'text/csv')



