# upload_server_files_gdrive.py

import os
import json
import time
import zipfile
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
from tqdm import tqdm
import utils

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
        SERVER_FILES_DIR = config['SERVER_FILES_DIR']
        SYNC_STATE_FILE = os.path.join(script_dir, 'sync_state.json')
        VERSION_LOG_FILE = os.path.join(script_dir, 'version_log.json')

        # Generate unique changes filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        changes_filename = f'changes_{timestamp}.zip'
        changes_zip_path = os.path.join(script_dir, changes_filename)

        

        # Load previous and current file states
        prev_states = utils.load_previous_file_states(SYNC_STATE_FILE)
        curr_states = utils.get_current_file_states(SERVER_FILES_DIR)

        # Identify changed files
        changed_files = [
            file for file in curr_states
            if file not in prev_states or curr_states[file] != prev_states[file]
        ]

        if changed_files:
            print("Changed files detected. Preparing to upload changes...")
            # Create zip of changed files
            with zipfile.ZipFile(changes_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in changed_files:
                    file_path = os.path.join(SERVER_FILES_DIR, file)
                    zipf.write(file_path, arcname=file)

            # Upload changes.zip to Google Drive
            file_metadata = {
                'name': changes_filename,
                'parents': [config['GDRIVE_FOLDER_ID']]
            }

            # Read the zip file in binary mode
            zip_size = os.path.getsize(changes_zip_path)
            fh = open(changes_zip_path, 'rb')

            # Create a MediaIoBaseUpload object with a resumable upload
            media = MediaIoBaseUpload(fh, mimetype='application/zip', resumable=True)

            request = service.files().create(body=file_metadata, media_body=media)
            print(f"Uploading '{changes_filename}' to Google Drive...")


            # Create a progress bar
            progress_bar = tqdm(total=zip_size, unit='B', unit_scale=True, desc='Uploading changes', ascii=True)


            # Upload the file in chunks
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress_bar.update(status.resumable_progress - progress_bar.n)
                time.sleep(0.1) # Delay to prevent spamming

            progress_bar.close()
            fh.close()

            # Remove the local changes zip file
            os.remove(changes_zip_path)

            if response: 
                print('Changes uploaded successfully')

            # Update version_log.json
            # First, download the existing version_log.json from Google Drive
            version_log = utils.download_version_log(service, config['GDRIVE_FOLDER_ID'], VERSION_LOG_FILE)

            # Append new change entry
            version_log.append({'timestamp' : timestamp, 'filename': changes_filename})

            # Upload updated version_log.json to Google Drive
            utils.upload_version_log(service, config['GDRIVE_FOLDER_ID'], VERSION_LOG_FILE, version_log)


            # Update sync_state.json
            utils.save_current_file_states(SYNC_STATE_FILE, curr_states)

        else:
            print('No changes detected. Skipping upload.')
    finally: 
        # Release lock
        utils.release_lock(service, config['GDRIVE_FOLDER_ID'])

if __name__ == '__main__':
    main()
