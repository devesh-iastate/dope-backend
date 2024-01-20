from fastapi import FastAPI, UploadFile, File, HTTPException, status, Form, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import aiohttp
from botocore.exceptions import NoCredentialsError
import logging
from utils import s3_client, verify_token, create_zip_in_memory, load_environment_variables

# Load environment variables
load_environment_variables()

# Create FastAPI instance
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

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 Client for AWS S3 / DigitalOcean Spaces
client = s3_client()


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
