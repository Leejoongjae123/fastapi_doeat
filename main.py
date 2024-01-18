import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pydantic
from fastapi import FastAPI
from mangum import Mangum

from fastapi import FastAPI
from mangum import Mangum


# process_drive(useremail='ljj90703001@gmail.com')


app=FastAPI()
handler=Mangum(app)
# @app.get('/')
# async def Hello():
#     return {"Hello":"World"}

@app.get("/")
async def process_user():
    return {"result": "Hello"}

@app.get("/getPath")
async def process_user(useremail: str):
    # Call the processing function with the received userId
    folderId=process_drive(useremail)
    return {"result": folderId}

def process_drive(useremail):
    # 서비스 계정 키 파일과 스코프 설정
    SERVICE_ACCOUNT_FILE = 'credential.json'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # 서비스 계정 인증 및 Drive API 클라이언트 구축
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    def create_folder(folder_name):
        """ 폴더 생성 함수 """
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        try:
            folder = service.files().create(body=file_metadata, fields='id').execute()
            print(f"Folder Created. ID: {folder.get('id')}")
            return folder.get('id')
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def share_folder(folder_id, user_email):
        """ 폴더에 사용자 권한 부여 함수 """
        # 권한을 부여할 이메일 주소 목록
        email_addresses = [user_email, 'uufkorea@gmail.com']
        for email in email_addresses:
          user_permission = {
              'type': 'anyone',
              'role': 'writer',  # 'reader', 'commenter', 'writer', 또는 'owner' 중 선택
              'emailAddress': email
          }
          try:
              service.permissions().create(
                  fileId=folder_id,
                  body=user_permission,
                  fields='id'
              ).execute()
              print(f"Folder shared ")
          except HttpError as error:
              print(f"An error occurred: {error}")

    def share_folder_publicly(folder_id):
        """ 폴더에 모든 사용자에게 권한 부여 함수 """
        public_permission = {
            'type': 'anyone',
            'role': 'writer'  # 'reader', 'commenter', 'writer', 또는 'owner' 중 선택
        }
        try:
            service.permissions().create(
                fileId=folder_id,
                body=public_permission,
                fields='id'
            ).execute()
            print("Folder shared with everyone.")
        except HttpError as error:
            print(f"An error occurred: {error}")

    # useremail='ljj90703001@gmail.com'
    timeNow=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_id = create_folder(useremail+timeNow)

    # share_folder(folder_id, useremail)  # 사용자 이메일 주소
    share_folder_publicly(folder_id)
    return 'https://drive.google.com/drive/folders/{}'.format(folder_id)

