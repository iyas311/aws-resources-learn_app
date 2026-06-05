from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File

from app.aws.s3 import upload_file
from app.aws.sns import publish_message
from app.aws.cloudwatch import logger

app = FastAPI(
    title="CloudLearn"
)


@app.get("/")
def home():

    return {
        "message": "CloudLearn Running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload(
        file: UploadFile = File(...)
):

    upload_file(
        file.file,
        file.filename
    )

    logger.info(
        f"Uploaded file {file.filename}"
    )

    return {
        "message": "File Uploaded"
    }


@app.get("/notify")
def notify():

    publish_message(
        "CloudLearn",
        "Test SNS Notification"
    )

    logger.info(
        "SNS Notification Sent"
    )

    return {
        "message": "SNS Sent"
    }


@app.get("/log")
def log_test():

    logger.info(
        "CloudWatch Test Log"
    )

    return {
        "message": "Log Created"
    }