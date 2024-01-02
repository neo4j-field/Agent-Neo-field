from scrape.scraper.scrape import GCPStorageLoader
import pandas as pd
import json

if __name__ == "__main__":
    loader = GCPStorageLoader()

    with open("scrape/scraper/resources/youtube_playlist_ids.json") as json_file:
        playlists = json.load(json_file)

    for title, id in playlists.items():
        # set playlist id
        loader.playlist_id = id
        loader._scraped_video_info = None
        print(title)
        print(loader.playlist_id)

        print("creating CSV file with video info...")
        # scrape video info for playlist
        loader.scrape_video_info(videos=[])

        print("uploading CSV file to Storage...")
        # upload to Storage
        loader.upload_scraped_video_info(file_name=title)

        print("Creating and uploading transcripts...")
        # create and upload transcripts
        loader.create_and_upload_neo4j_transcripts(transcripts_folder=title, video_info_file_name=title)

        # ignore failed for now

        print()