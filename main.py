from fastapi import FastAPI, File, UploadFile
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()


# Replace these with your DigitalOcean Spaces credentials
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')

s3 = boto3.client(
    's3',
    # Replace with your Spaces region's endpoint
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        s3.upload_fileobj(
            file.file,
            BUCKET_NAME,
            file.filename,
        )
        return {"message": "File uploaded successfully"}
    except NoCredentialsError:
        return {"error": "No AWS credentials found"}
