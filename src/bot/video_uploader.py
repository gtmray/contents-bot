import os
import logging.config
from typing import Optional
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

logging.config.fileConfig("../config/logging_config.ini")
logger = logging.getLogger()


# Constants
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE")
TOKEN_FILE = os.getenv("TOKEN_FILE")
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def authenticate(scopes: list[str]) -> Credentials:
    """
    Handles user authentication and returns credentials.
    """
    creds: Optional[Credentials] = None

    # Load credentials if available
    if os.path.exists(TOKEN_FILE):
        logger.info(f"Loading credentials from {TOKEN_FILE}")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)

    # If no valid credentials, authenticate via OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            logger.info("Initiating OAuth flow for new credentials")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, scopes
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(TOKEN_FILE, "w") as token:
            logger.info(f"Saving credentials to {TOKEN_FILE}")
            token.write(creds.to_json())

    return creds


def get_authenticated_service():
    """
    This function uses the authenticate function to obtain the necessary
    credentials and then builds the YouTube API service using the
    googleapiclient.discovery.build method.

    Returns:
        googleapiclient.discovery.Resource: An authenticated
        YouTube API service resource.
    """
    try:
        logger.info("Authenticating and obtaining credentials...")
        credentials = authenticate([YOUTUBE_UPLOAD_SCOPE])
        logger.info("Building the YouTube API service...")
        youtube_service = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            credentials=credentials,
        )
        logger.info("YouTube API service built successfully.")
        return youtube_service
    except Exception as e:
        logger.error(
            f"An error occurred while building the YouTube API service: {e}"
        )
        raise


def upload_video(
    youtube,
    file_path: str,
    title: str,
    description: str,
    privacy_status: str = "private",
):
    """
    Uploads a video to YouTube.
    Args:
        youtube: The authenticated YouTube service instance.
        file_path (str): The path to the video file to be uploaded.
        title (str): The title of the video.
        description (str): The description of the video.
        privacy_status (str, optional): The privacy status of the video.
        Defaults to "private".

    Returns:
        None
    """
    if not os.path.exists(file_path):
        logger.error(f"The file '{file_path}' does not exist.")
        return

    body = {
        "snippet": {
            "title": title,
            "description": description,
        },
        "status": {"privacyStatus": privacy_status},
    }

    media_body = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    try:
        logger.info("Uploading video...")
        request = youtube.videos().insert(
            part="snippet,status", body=body, media_body=media_body
        )
        response = request.execute()
        logger.info(
            f"Video uploaded successfully. Video ID: {response['id']}."
        )
        logger.info(
            f"Video URL: https://www.youtube.com/watch?v={response['id']}"
        )
    except Exception as e:
        logger.error(f"An error occurred during upload: {e}")


def get_video_details(youtube, video_id: str):
    """
    Fetches and prints details of a YouTube video.
    Args:
        youtube: The authenticated YouTube service instance.
        video_id (str): The ID of the YouTube video.
    """
    try:
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            video = response["items"][0]
            title = video["snippet"]["title"]
            description = video["snippet"]["description"]
            statistics = video.get("statistics", {})

            logger.info(f"Title: {title}")
            logger.info(f"Description: {description}")
            logger.info(
                f"Views: {statistics.get('viewCount', 'Not available')}"
            )
            logger.info(
                f"Likes: {statistics.get('likeCount', 'Not available')}"
            )
            logger.info(
                f"Comments: {statistics.get('commentCount', 'Not available')}"
            )
        else:
            logger.warning("Video not found or has no details.")
    except Exception as e:
        logger.error(f"An error occurred while fetching video details: {e}")


if __name__ == "__main__":
    video_file = "./outputs/v1.mp4"
    title = "My Video Title"
    description = "This is a description of my video"
    privacy_status = "private"

    # Authenticate and upload
    youtube_service = get_authenticated_service()
    logger.info("Uploading video...")
    upload_video(
        youtube_service, video_file, title, description, privacy_status
    )

    # # Fetch video details
    # video_id = "XyxBMmiH_F4"
    # logger.info("Fetching video details...")
    # get_video_details(youtube_service, video_id)
