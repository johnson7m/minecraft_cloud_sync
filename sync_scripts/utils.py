# utils.py

import os
import json
import sys
import io
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload


def get_file_state(file_path):
    """Get the modification time of a file."""
    mod_time = os.path.getmtime(file_path)
    return mod_time

def get_current_file_states(root_dir):
    """Get the modification times of all files in the directory."""
    file_states = {}
    for root, _, files in os.walk(root_dir):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, root_dir)
            file_states[relative_path] = get_file_state(file_path)
    return file_states

def load_previous_file_states(state_file):
    """Load previous file states from a JSON file."""
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                data = f.read().strip()
                if not data:
                    return {}
                return json.loads(data)
        except json.JSONDecodeError:
            print(f"Warning: '{state_file}' is not a valid JSON file. Proceeding with empty previous states.")
            return {}
        except Exception as e:
            print(f"Error reading '{state_file}': {e}")
            return {}
    else:
        return {}

def save_current_file_states(state_file, file_states):
    """Save current file states to a JSON file."""
    import tempfile
    import shutil

    temp_file = state_file + '.tmp'
    try:
        with open(temp_file, 'w') as f:
            json.dump(file_states, f, indent=4)
        shutil.move(temp_file, state_file)
    except Exception as e:
        print(f"Error writing to '{state_file}': {e}")


def is_locked(service, folder_id):
    query = f"name = 'sync.lock' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    return len(results.get('files', [])) > 0

def acquire_lock(service, folder_id):
    if is_locked(service, folder_id):
        print("Another synchronization is in progress. Exiting.")
        sys.exit(1)
    file_metadata = {
        'name': 'sync.lock',
        'parents': [folder_id],
        'mimeType': 'application/vnd.google-apps.document'  # Using a Google Doc as a lock file
    }
    service.files().create(body=file_metadata, fields='id').execute()
    print("Lock acquired.")

def release_lock(service, folder_id):
    query = f"name = 'sync.lock' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    for file in results.get('files', []):
        service.files().delete(fileId=file['id']).execute()
    print("Lock released.")

def download_version_log(service, folder_id, local_version_log_path):
    # Check if version_log.json exists on Google Drive
    query = f"name = 'version_log.json' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id,name)').execute()
    items = results.get('files', [])
    
    if items:
        print("Download 'version_log.json' from Google Drive...")
        file_id = items[0]['id']
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        version_log = json.load(fh)

        # Save local copy
        with open(local_version_log_path, 'w') as f:
            json.dump(version_log, f, indent=4)

        return version_log
    else: 
        print("'version_log.json' not found on Google Drive. Starting with an empty version log.")
        return []
    
def upload_version_log(service, folder_id, local_version_log_path, version_log):
    # Update local version_log.json
    with open(local_version_log_path, 'w') as f:
        json.dump(version_log, f, indent=4)

    # Check if version_log.json exists on Google Drive
    query = f"name = 'version_log.json' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    file_metadata = {
        'name': 'version_log.json',
        'parents': [folder_id]
    }

    media = MediaIoBaseUpload(io.BytesIO(json.dumps(version_log).encode('utf-8')), mimetype='application/json')

    if items:
        # Update existing version_log.json
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print("'version_log.json' updated on Google Drive")
    else:
        # Upload new version_log.json
        service.files().create(body=file_metadata, media_body=media).execute()
        print("'version_log.json' uploaded to Google Drive.")