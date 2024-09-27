import json
import os

def main():
    config = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get Google Drive folder ID
    config['GDRIVE_FOLDER_ID'] = input("Enter the Google Drive folder ID for synchronization: ").strip()

    # Set local directories
    base_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
    config['SERVER_FILES_DIR'] = os.path.join(base_dir, 'server_files')
    config['BACKUP_DIR'] = os.path.join(base_dir, 'backup')

    # Files for authentication
    config['CREDENTIALS_FILE'] = os.path.join(script_dir, 'credentials.json')
    config['TOKEN_FILE'] = os.path.join(script_dir, 'token.json')

    # Save config
    config_path = os.path.join(script_dir, 'config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    print(f"Configuration saved to {config_path}")

if __name__ == '__main__':
    main()
