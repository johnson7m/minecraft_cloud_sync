# Minecraft Server Synchronization via Google Drive

## Introduction

This project allows multiple trusted users to host and synchronize a Minecraft server using Google Drive. By leveraging cloud storage, all users can keep their server files up-to-date, ensuring a seamless multiplayer experience without the hassle of manually sharing and updating files.

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Python Dependencies](#2-install-python-dependencies)
  - [3. Set Up Google Cloud API Credentials](#3-set-up-google-cloud-api-credentials)
  - [4. Prepare Your Minecraft Server Files](#4-prepare-your-minecraft-server-files)
  - [5. Upload Initial Server Files to Google Drive](#5-upload-initial-server-files-to-google-drive)
  - [6. Share the Google Drive Folder](#6-share-the-google-drive-folder)
  - [7. Distribute the Project to Trusted Users](#7-distribute-the-project-to-trusted-users)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Server](#running-the-server)
- [Versioning](#versioning)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Operating System**: Windows (due to the use of batch scripts)
- **Python**: Version 3.6 or higher (Python 3.12 recommended)
- **Java**: Installed and added to your system's PATH (required to run the Minecraft server)
- **Google Account**: For accessing Google Drive API
- **Google Cloud Project**: Set up with Google Drive API enabled
- **Minecraft Server**: A working Minecraft server setup
- **Port Forwarding**: Port 25565 forwarded on your router for hosting the server
- **Trustworthy Collaborators**: Only share this project with users you fully trust

## Setup and Installation

Follow these steps to set up the project:

### 1. Clone the Repository

Clone this repository to your local machine:

``` bash 
git clone https://github.com/yourusername/yourrepository.git
```

Replace `yourusername` and `yourrepository` with your actual GitHub username and repository name.

### 2. Install Python Dependencies

Navigate to the project directory and install the required Python packages:

``` bash
cd yourrepository pip install -r requirements.txt
```

### 3. Set Up Google Cloud API Credentials

#### a. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.

#### b. Enable Google Drive API

1. In the Cloud Console, navigate to **APIs & Services** > **Library**.
2. Search for **Google Drive API** and enable it.

#### c. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**.
2. Choose **External** for the user type and click **Create**.
3. Fill in the required app information.
4. Under **Scopes**, add the following scope:
   - `https://www.googleapis.com/auth/drive.file`
5. Under **Test users**, add the email addresses of your trusted users.

#### d. Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Click **Create credentials** > **OAuth client ID**.
3. Select **Desktop app** as the application type.
4. Name it (e.g., `Minecraft Server Sync`) and click **Create**.
5. Download the `credentials.json` file and place it in the `sync_scripts` folder of your project.

### 4. Prepare Your Minecraft Server Files

1. **Rename Your Server Folder**: Rename your existing Minecraft server folder to `server_files`.
2. **Place `server_files` in Project Directory**: Move the `server_files` folder into the root directory of the cloned repository (alongside `sync_scripts` and other files).
3. **Ensure Correct Folder Structure**:

``` text
yourrepository/
├── backup/
├── server_files/
├── sync_scripts/
├── run_all.bat
├── requirements.txt
└── ...
```

4. **Rename the Parent Folder**: Ensure the parent folder is named `minecraft_server`.

### 5. Upload Initial Server Files to Google Drive

To allow other users to initialize the server with the same baseline:

1. **Create a Zip Archive**:

- Compress the `server_files` folder into a zip file named `server_files.zip`.

2. **Create a Shared Folder on Google Drive**:

- In your Google Drive, create a new folder (e.g., `Minecraft Server Sync`).
- Note the **Folder ID**, which is the part of the URL after `folders/`. It should look like `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`.

3. **Upload `server_files.zip` to the Google Drive Folder**:

- Upload the `server_files.zip` file to the shared folder you just created.

### 6. Share the Google Drive Folder

Share the Google Drive folder with your trusted users:

1. Right-click the folder and select **Share**.
2. Add the email addresses of your trusted users (they must be the same emails added as test users in your Google Cloud project).
3. Give them **Editor** access.

### 7. Distribute the Project to Trusted Users

Provide your trusted users with a copy of the project:

- **Exclude Sensitive Files**:

- Do **not** include `token.json` or `config.json` (these are generated per user).
- Do **not** include your `server_files` folder (each user will download it from Google Drive).
- **Securely** share the `credentials.json` file or instruct users to obtain their own.

- **Provide Instructions**:

- Include this README and any additional instructions.

## Configuration

Each user needs to perform some configuration steps:

1. **Place `credentials.json` in `sync_scripts` Folder**:

- Obtain the `credentials.json` file (from Google Cloud Console or securely from you).
- Place it in the `sync_scripts` folder.

2. **Run `run_all.bat`**:

- Double-click `run_all.bat` in the root project directory.
- The script will guide the user through the setup process.

3. **Enter the Google Drive Folder ID**:

- When prompted, enter the `GDRIVE_FOLDER_ID` (the ID of the shared Google Drive folder).

4. **Authenticate with Google Drive**:

- A browser window will open prompting the user to authenticate.
- Log in with the Google account that has access to the shared folder.

5. **Backup Option**:

- The script will ask if you want to create a backup of your server files.
- Choose **yes** to create a local backup (recommended).

6. **Initialization**:

- The script will detect that no local server files are present and will download `server_files.zip` from Google Drive.
- The server files will be extracted, and the synchronization state will be initialized.

## Usage

### Running the Server

Always start the server using the `run_all.bat` script to ensure synchronization occurs:

1. **Start the Server**:

- Double-click `run_all.bat`.
- The script will synchronize files from Google Drive, prompt for a backup, and start the server.

2. **Play on the Server**:

- Connect to the server as usual.
- Remember to use the `stop` command in the server console to shut down the server properly.

3. **After Stopping the Server**:

- Upon exiting the server, the script will automatically upload any changes to Google Drive.
- The first upload may be large if the sync state is being initialized. Subsequent uploads will only include changes.

**Important**: Do not run the server directly from `server_files/run.bat` as this will bypass the synchronization scripts.

## Versioning

This project uses incremental changes to synchronize server files. Each set of changes is uploaded as a `changes_timestamp.zip` file to Google Drive, and a `version_log.json` keeps track of versions.

**Note**: The synchronization process is somewhat fragile in this initial version. It is crucial to follow the setup and usage instructions carefully to avoid issues such as large unnecessary uploads.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [Google Drive API](https://developers.google.com/drive)
- [Python](https://www.python.org/)
- [Minecraft](https://www.minecraft.net/)
- [tqdm](https://tqdm.github.io/) for progress bars in the scripts

---
 
**Disclaimer**: This is an initial working version of the project. Future updates may automate and simplify the setup process. Always ensure you trust the users you share this project with, as they will have access to your server files.

---
 
If you have any questions or encounter issues, please feel free to open an issue on the GitHub repository.
