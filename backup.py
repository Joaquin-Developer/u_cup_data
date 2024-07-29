import logging
from datetime import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


CREDENTIALS_FILE = "credentials.json"
BACKUP_DIR = "/home/jparilla/Documents/personal/u_cup/database/backups"
GOOGLE_DRIVE_FOLDER_ID = "1bIE9Hu4n6g7e6UxMKS5PqAPBFipLPEtJ"


logging.basicConfig(level=logging.INFO)


def get_file_name() -> str:
    actual_date = datetime.now().strftime("%Y-%m-%d")
    return f"{BACKUP_DIR}/{actual_date}.sql.gz"


def upload_to_drive(filepath: str, file_name: str):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if not gauth.credentials:
        gauth.LoadClientConfigFile("credentials.json")
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")
    elif gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile("mycreds.txt")
    else:
        gauth.Authorize()

    drive = GoogleDrive(gauth)
    file = drive.CreateFile({"title": file_name, "parents": [{"id": GOOGLE_DRIVE_FOLDER_ID}]})

    file.SetContentFile(filepath)
    file.Upload()
    logging.info("OK")


def main():
    try:
        backup_file = get_file_name()
        drive_file_name = backup_file.split("/")[-1]
        upload_to_drive(backup_file, drive_file_name)
    except Exception as error:
        logging.error(error)
        raise


if __name__ == "__main__":
    main()
