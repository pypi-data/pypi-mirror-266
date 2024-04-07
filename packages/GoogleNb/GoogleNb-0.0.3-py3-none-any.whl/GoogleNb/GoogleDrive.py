import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class GoogleDrive:

    CREDS           = None
    SERVICE         = None
    SCOPE           = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, key : str = ""):
        """
            Creates a GoogleDrive instance.
            
            Args:
                key (str)           : The path to the service account json file.
        """
        try:
            self.CREDS          = service_account.Credentials.from_service_account_file(key, scopes=self.SCOPE)
            self.SERVICE        = build("drive", "v3", credentials=self.CREDS)
        except Exception as e:
            print({
                "error"     : True,
                "response"  : str(e)
            })
            exit(1)

    def getFile(self, id) -> str:
        """
            Add data to the sheet.
            
            Args:
                id (str)            : Id file.

            Returns:
                byte                : return response of the file
        """
        try:
            request                 = self.SERVICE.files().get_media(fileId = id)
            file                    = io.BytesIO()
            downloader              = MediaIoBaseDownload(file, request)
            done                    = False
            while done is False:
                status, done        = downloader.next_chunk()
            return file.getvalue()
        except Exception as e:
            return {
                "error"     : True,
                "response"  : str(e)
            }