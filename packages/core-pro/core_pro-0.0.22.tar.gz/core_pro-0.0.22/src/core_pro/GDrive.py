import io
from colorama import Fore
import mimetypes
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from pathlib import Path
from .config import GoogleAuthentication


class Drive(GoogleAuthentication):
    service_type = 'drive'

    def __init__(self, service_type=service_type):
        super().__init__(service_type)
        self.status = f'{Fore.LIGHTRED_EX}🦑 Drive:{Fore.RESET}'

    def upload(
            self,
            file_dir: Path,
            folder_id: str,
            name_on_drive: str = None,
    ) -> str:
        """Upload to drive"""
        # init
        if not name_on_drive:
            name_on_drive = file_dir.name
        file_dir = file_dir.resolve()
        # get info
        file_metadata = {'name': name_on_drive, 'parents': [folder_id]}
        content_type, _ = mimetypes.guess_type(file_dir)
        media = MediaFileUpload(file_dir, mimetype=content_type)
        fields = 'webContentLink, id, webViewLink'
        # upload
        file = self.service.files().create(body=file_metadata, media_body=media, fields=fields).execute()
        print(f"{self.status} Successfully uploaded, folder_id: {folder_id}")
        return file

    def get_file_info(self, file_id):
        fields = 'id,name,mimeType,kind,size,fileExtension'
        return self.service.files().get(fileId=file_id, fields=fields).execute()

    def drive_download(
            self,
            file_id: str,
            download_dir: str
    ):
        """Download from drive"""
        # get info
        file_info = self.get_file_info(file_id)
        save_path = f"{download_dir}/{file_info['name']}"
        # download
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(save_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Drive Download {int(status.progress() * 100)}%")
        print(f"{self.status} Successfully downloaded, path: {save_path}")
        return save_path

    def create_new_folder(
            self,
            name: str,
            parent_id=None
    ):
        """
        create new folder on Google Drive
        :param name: Name of folder
        :param parent_id: id of parent folder , default None
        :return: return folder id if True
        """

        file_metadata = {
            'name': name,
            'parents': [parent_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if not parent_id:
            file_metadata.pop('parents')
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        print(f"{self.status} Successfully created folder: {name} - Folder ID: {file.get('id')}")
        return file.get('id')

    def rename_drive_file(self, spreadsheet_id, new_name):
        file = {'name': new_name}
        self.service.files().update(fileId=spreadsheet_id, body=file).execute()

    def download_gsheet(self, file_id, file_location, file_name, file_type):
        request = self.service.files().export_media(fileId=file_id, mimeType=file_type)
        fh = io.FileIO(file_location + file_name, mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    def search_files(self, folder_id):
        fields = 'nextPageToken, files(id, name, createdTime, modifiedTime)'
        results = self.service.files().list(q=f"'{folder_id}' in parents and trashed=false", fields=fields).execute()
        return results.get('files', [])

    def share_file(
            self,
            file_id,
            email: str = None,
            role: str = 'reader',
            domain: str = '@shopee.com'
    ):
        """
        :param file_id: abc
        :param email: abc@example.com
        :param role: reader/writer
        :param domain: @example.com
        :return: text
        """
        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(exception)
            else:
                print(f"Request_Id: {request_id}")
                print(f'Permission Id: {response.get("id")}')
                ids.append(response.get("id"))

        ids = []
        batch = self.service.new_batch_http_request(callback=callback)
        if email:
            permission = {
                "type": "user",
                "role": role,
                "emailAddress": email,
            }
            batch.add(self.service.permissions().create(fileId=file_id, body=permission, fields="id"))
        else:
            permission = {
                "type": "domain",
                "role": role,
                "domain": domain,
            }
            batch.add(self.service.permissions().create(fileId=file_id, body=permission, fields="id"))
        batch.execute()
        print(f"{self.status} Shared {permission['type']} {permission.get('emailAddress', 'domain')}: {file_id}")

    def remove_share_publicly(self, file_id):
        self.service.permissions().delete(fileId=file_id, permissionId='anyoneWithLink', fields='id').execute()
        print(f"{self.status} Removed sharing: {file_id}")
