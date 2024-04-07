import io
import os
import sys

import frontmatter
import markdown

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from md2gdocs import config, logging

AUTH_PROMPT_MESSAGE = "Opening browser for authentication ... \n"
AUTH_SUCCESS_MESSAGE = "Successfully authenticated (you may now close this browser window)."
DOCS_VERSION, DRIVE_VERSION = "v1", "v3"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def cli():
    try:
        md_file_path = sys.argv[1]
    except IndexError:
        logging.error("Please provide the path to a markdown file as the first argument.")
        raise SystemExit(1)
    try:
        convert_and_upload(md_file_path)
    except Exception as ex:
        logging.error(f"Failed to convert and upload {md_file_path}. {ex}")
        raise SystemExit(2)


def convert_and_upload(md_file_path):
    logging.info(f"converting {md_file_path} to HTML ... ")
    html_content = markdown_to_html(md_file_path)
    try:
        metadata = get_document_metadata(md_file_path)
        if id := metadata.get("gdrive_id"):
            if title := metadata.get("title"):
                update_gdoc_from_html(id, html_content, title=title)
            else:
                update_gdoc_from_html(id, html_content)
        else:
            if title := metadata.get("title"):
                gdoc = create_gdoc_from_html(html_content, title)
                add_document_id(md_file_path, gdoc["id"])
            else:
                raise RuntimeError("Document must have a title to publish to Google Docs!")
    except Exception as ex:
        raise RuntimeError(f"There was an error uploading to Google Drive. {ex}")


def markdown_to_html(md_file_path):
    extensions = list(set(config.get("markdown.extensions")[:] + ["meta"]))
    if not os.path.isfile(md_file_path):
        raise RuntimeError(f"File {md_file_path} does not exist! Please try again.")
    try:
        with open(md_file_path, "r") as _mdfile:
            markdown_content = _mdfile.read()
    except UnicodeDecodeError:
        raise RuntimeError(f"Could not open file (expecting utf8 text but got binary instead).")
    try:
        return io.BytesIO(
            bytes(markdown.markdown(markdown_content, extensions=extensions), encoding="utf8")
        )
    except Exception as ex:
        raise RuntimeError(f"Error converting markdown to HTML. Please check your content. {ex}")


def get_document_metadata(md_file_path):
    with open(md_file_path) as _mdfile:
        metadata, _ = frontmatter.parse(_mdfile.read())
    return metadata


def update_gdoc_from_html(gdrive_id, html_content, title=None):
    drive = authenticate_google_drive()
    if title:
        file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    else:
        file_metadata = {"mimeType": "application/vnd.google-apps.document"}
    media = MediaIoBaseUpload(html_content, mimetype="text/html", resumable=True)
    drive_file = (
        drive.files().update(fileId=gdrive_id, body=file_metadata, media_body=media).execute()
    )
    return drive_file


def create_gdoc_from_html(html_content, title):
    drive = authenticate_google_drive()
    file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    media = MediaIoBaseUpload(html_content, mimetype="text/html", resumable=True)
    drive_file = drive.files().create(body=file_metadata, media_body=media).execute()
    return drive_file


def add_document_id(md_file_path, id):
    doc = frontmatter.load(md_file_path)
    doc["gdrive_id"] = id
    frontmatter.dump(doc, md_file_path)


def authenticate_google_drive():
    credentials = None
    token_file = config.get("google.oauth.token")
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, scopes=SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.get("google.oauth.client_credentials"), scopes=SCOPES
            )
            credentials = flow.run_local_server(
                host="localhost",
                port=config.get("google.oauth.server_port"),
                authorization_prompt_message=AUTH_PROMPT_MESSAGE,
                success_message=AUTH_SUCCESS_MESSAGE,
                open_browser=True,
            )
        with open(token_file, "w") as _token:
            _token.write(credentials.to_json())
    return build("drive", DRIVE_VERSION, credentials=credentials)


if __name__ == "__main__":
    cli()
