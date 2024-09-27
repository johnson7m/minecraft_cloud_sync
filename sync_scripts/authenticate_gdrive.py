import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

def main():
    # Load configuration
    script_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(script_dir, 'config.json'), 'r') as f:
        config = json.load(f)

    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    token_path = config['TOKEN_FILE']
    credentials_path = config['CREDENTIALS_FILE']

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    print("Authentication successful.")

if __name__ == '__main__':
    main()
