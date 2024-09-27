# download_server_files_gdrive.py

import os
import sys
import json
import io
import zipfile
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from tqdm import tqdm
import utils


def backup_server_files(server_files_dir, backup_dir):
    # Check if server_files_dir exists and is not empty
    if os.path.exists(server_files_dir) and os.listdir(server_files_dir):
        # Ask for user confirmation with a loop for valid responses
        while True:
            confirm = input("Do you want to create a backup? (yes/no): ").strip().lower()
            if confirm in ['yes', 'no']:
                break
            print("Invalid input. Please enter 'yes' or 'no'.")
        
        if confirm == 'yes':
            backup_zip_name = 'backup_latest.zip'  # Overwrite the last backup
            backup_zip_path = os.path.join(backup_dir, backup_zip_name)
            print(f"Creating backup of server files at {backup_zip_path}...")
            os.makedirs(backup_dir, exist_ok=True)
            with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(server_files_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, server_files_dir)
                        zipf.write(file_path, arcname=arcname)
            print("Backup completed and overwritten the previous backup.")
        else:
            print("Backup operation canceled by the user.")
    else:
        print("No existing server files to backup.")

def main():
    # Load configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, 'config.json'), 'r') as f:
        config = json.load(f)

    creds = Credentials.from_authorized_user_file(config['TOKEN_FILE'], ['https://www.googleapis.com/auth/drive.file'])
    service = build('drive', 'v3', credentials=creds)

    # Acquire lock
    utils.acquire_lock(service, config['GDRIVE_FOLDER_ID'])

    try:
        # Define file names and paths
        BACKUP_DIR = config['BACKUP_DIR']        
        SERVER_FILES_DIR = config['SERVER_FILES_DIR']
        SYNC_STATE_FILE = os.path.join(script_dir, 'sync_state.json')
        VERSION_LOG_FILE = os.path.join(script_dir, 'version_log.json')

        # Backup server files before applying new changes
        backup_server_files(SERVER_FILES_DIR, BACKUP_DIR)

        # First-time setup: Check if server files exist
        if not os.path.exists(SERVER_FILES_DIR) or not os.listdir(SERVER_FILES_DIR):
            print("No server files found locally. Downloading full server files...")
            SERVER_ZIP_NAME = 'server_files.zip'


            print(f"SERVER_ZIP_NAME: {SERVER_ZIP_NAME}")
            print(f"GDRIVE_FOLDER_ID: {config['GDRIVE_FOLDER_ID']}")
            print(f"Query: name = '{SERVER_ZIP_NAME}' and '{config['GDRIVE_FOLDER_ID']}' in parents and trashed = false")


            # Find the server zip file in Google Drive
            query = f"name = '{SERVER_ZIP_NAME}' and '{config['GDRIVE_FOLDER_ID']}' in parents and trashed = false"
            results = service.files().list(q=query, spaces='drive', fields='files(id, name, size)').execute()
            items = results.get('files', [])

            if not items:
                print(f"No '{SERVER_ZIP_NAME}' found in Google Drive folder.")
                sys.exit(0)

            file_id = items[0]['id']
            file_size = int(items[0].get('size', 0))

            # Prepare the download request
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)  # 1MB chunks

            print(f"Downloading '{SERVER_ZIP_NAME}' from Google Drive...")
            # Create a progress bar
            progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc='Downloading server files', ascii=True)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    progress_bar.update(status.resumable_progress - progress_bar.n)
            progress_bar.close()

            # Extract the zip file
            fh.seek(0)
            with zipfile.ZipFile(fh, 'r') as zip_ref:
                zip_ref.extractall(SERVER_FILES_DIR)
            print(f"Server files downloaded and extracted to {SERVER_FILES_DIR}")

            # Update sync_state.json
            curr_states = utils.get_current_file_states(SERVER_FILES_DIR)
            utils.save_current_file_states(SYNC_STATE_FILE, curr_states)        


        # Load local version log
        if os.path.exists(VERSION_LOG_FILE):
            with open(VERSION_LOG_FILE, 'r') as f:
                local_version_log = json.load(f)
        else: 
            local_versoin_log = []

        
        # Download the latest version_log.json from Google Drive
        version_log = utils.download_version_log(service, config['GDRIVE_FOLDER_ID'], VERSION_LOG_FILE)

        # Determine which changes need to be applied
        local_versions = {entry['timestamp'] for entry in local_version_log}
        remote_versions = {entry['timestamp'] for entry in version_log}

        missing_versions = [entry for entry in version_log if entry['timestamp'] not in local_version_log]

        if missing_versions: 
            print("New changes detected. Downloading and applying updates...")
            # Sort missing_versions by timestamp to apply them in order
            missing_versions.sort(key=lambda x: x['timestamp'])
            for entry in missing_versions:
                changes_filename = entry['filename']
                # Download changes_<timestamp>.zip
                query = f"name = '{changes_filename}' and '{config['GDRIVE_FOLDER_ID']}' in parents and trashed = false"
                results = service.files().list(q=query, spaces='drive', fields='files(id, name, size)').execute()
                items = results.get('files', [])

                if items:
                    print(f"Downloading '{changes_filename}' from Google Drive...")
                    file_id = items[0]['id']
                    file_size = int(items[0].get('size', 0))

                    # Prepare the download request
                    request = service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request, chunksize=1024*1024)  # 1MB chunks

                    # Create a progress bar
                    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc='Downloading changes', ascii=True)

                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                        if status:
                            progress_bar.update(status.resumable_progress - progress_bar.n)
                    progress_bar.close()

                    # Apply changes from changes.zip
                    fh.seek(0)
                    with zipfile.ZipFile(fh, 'r') as zip_ref:
                        zip_ref.extractall(SERVER_FILES_DIR)
                    print("Changes applied successfully.")

                    # Optionally delete the changes file from Google Drive after applying
                    # service.files().delete(fileId=file_id).execute()
                    # print(f"'{changes_filename}' removed from Google Drive.")

                    # Update local version log
                    local_version_log.append(entry)
                    with open(VERSION_LOG_FILE, 'w') as f:
                        json.dump(local_version_log, f, indent=4)

                else:
                    print(f"Error: '{changes_filename}' not found on Google Drive.")

            # Update sync_state.json
            curr_states = utils.get_current_file_states(SERVER_FILES_DIR)
            utils.save_current_file_states(SYNC_STATE_FILE, curr_states)

        else:
            print("No new changes to apply.")

    finally:
        # Release lock
        utils.release_lock(service, config['GDRIVE_FOLDER_ID'])

if __name__ == '__main__':
    main()
