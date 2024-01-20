from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form, Response, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import aiohttp
import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO
import zipfile
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI app instance
app = FastAPI()

# Configure CORS
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')
admin_username = os.getenv('admin_username')
admin_apiKey = os.getenv('admin_apiKey')
GROUP_ID = os.getenv('GROUP_ID')
APP_ID = os.getenv('APP_ID')

# boto3 client for interacting with AWS S3 (DigitalOcean Spaces in this case)
client = boto3.client(
    's3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# Async function to verify user token using MongoDB Realm
async def verify_token(token: str) -> bool:
    admin_token_url = "https://realm.mongodb.com/api/admin/v3.0/auth/providers/mongodb-cloud/login"
    data = {
        "username": admin_username,
        "apiKey": admin_apiKey
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(admin_token_url, json=data) as response:
                if response.status != 200:
                    return False
                admin_token = await response.json()

        admin_access_token = admin_token["access_token"]
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        }
        payload = json.dumps({
            "token": token
        })
        client_verify_token_url = f"https://realm.mongodb.com/api/admin/v3.0/groups/{GROUP_ID}/apps/{APP_ID}/users/verify_token"

        async with aiohttp.ClientSession() as session:
            async with session.post(client_verify_token_url, headers=headers, data=payload) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return False


@app.post("/api/upload_file/")
async def upload_file(folder: str = Form(...), token: str = Form(...), file: UploadFile = File(...)):
    try:
        # Verify token
        if not await verify_token(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Upload file to S3 and local storage
        await upload_file_to_storage(client, folder, file)
        
        return JSONResponse(content={"message": "File uploaded successfully!"}, status_code=200)
    except NoCredentialsError:
        logger.error("No AWS credentials found")
        return JSONResponse(content={"error": "No AWS credentials found"}, status_code=500)
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/generate_download_link/")
async def generate_download_link(request: Request):
    body = await request.json()
    file_path = body.get('filePath')
    token = body.get('token')
    
    # Verify token
    if not await verify_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Generate and return presigned URL
    try:
        url = generate_presigned_url(client, file_path)
        return JSONResponse(content={"url": url}, status_code=200)
    except Exception as e:
        logger.error(f"Error generating download link: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/download_folder/")
async def download_folder(request: Request):
    try:
        body = await request.json()
        folder = body.get('folder')
        token = body.get('token')
        
        # Verify token
        if not await verify_token(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Create zip file in memory
        zip_content, file_name = create_zip_in_memory(client, folder)
        
        headers = {
            'Content-Disposition': f'attachment; filename={file_name}'
        }
        
        return Response(content=zip_content.getvalue(), media_type="application/zip", headers=headers)
    except NoCredentialsError:
        logger.error("No AWS credentials found")
        return JSONResponse(content={"error": "No AWS credentials found"}, status_code=500)
    except Exception as e:
        logger.error(f"Error downloading folder: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/hello/")
async def hello(req):
    return "hello"


# Entry point for running the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
