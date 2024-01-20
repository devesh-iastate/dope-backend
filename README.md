# DOPE - Backend

## Overview
This application provides a FastAPI server for handling file uploads, downloads, and management with DigitalOcean Spaces as the storage backend. It includes authentication and token verification using MongoDB Realm, ensuring secure access to the APIs.

## Features
- **File Upload:** Allows users to upload files to specific folders in DigitalOcean Spaces.
- **File Download:** Enables the creation of downloadable presigned URLs for files stored in DigitalOcean Spaces.
- **Folder Download:** Facilitates downloading an entire folder as a zip file from DigitalOcean Spaces.
- **Authentication:** Utilizes MongoDB Realm for verifying user tokens, ensuring secure access to the application's functionalities.

## Prerequisites
- Python 3.10+
- Docker (for containerization)
- DigitalOcean Spaces account with API access
- MongoDB Realm account

## Installation & Setup
1. **Clone the Repository**
    ```
    git clone [https://github.com/devesh-iastate/dope-backend.git]
    cd dope-backend
    ```

2. **Set Environment Variables**
    Copy the `.env.example` file to `.env` and fill in your DigitalOcean Spaces and MongoDB Realm credentials:
    ```
    ACCESS_KEY = [your_access_key]
    SECRET_KEY = [your_secret_key]
    BUCKET_NAME = [your_bucket_name]
    GROUP_ID = [your_group_id]
    APP_ID = [your_app_id]
    admin_username = [your_admin_username]
    admin_apiKey = [your_admin_apiKey]
    ```

3. **Build and Run the Docker Container**
    ```
    docker build -t fastapi-file-manager .
    docker run -d -p 8000:8000 fastapi-file-manager
    ```

## API Endpoints
- `POST /api/upload_file/`: Upload a file to a specified folder in DigitalOcean Spaces.
- `POST /api/generate_download_link/`: Generate a downloadable presigned URL for a specific file in DigitalOcean Spaces.
- `POST /api/download_folder/`: Download an entire folder as a zip file from DigitalOcean Spaces.
- `GET /api/hello/`: Simple endpoint to check if the server is running.

## Running Locally
To run the application locally without Docker:
```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Notes
- Ensure that your `.env` file is properly configured with the correct credentials and parameters.
- The application uses CORSMiddleware, allowing cross-origin requests from all origins. Modify this in `app.py` if necessary.

## License
[MIT License](LICENSE) or your preferred license.

