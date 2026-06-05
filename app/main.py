from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi.responses import StreamingResponse

from app.aws.s3 import upload_file, list_files, get_object, generate_presigned_url
from app.aws.sns import publish_message
from app.aws.cloudwatch import logger
from app.aws.metrics import put_metric

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

    put_metric("HealthChecks")

    return {
        "status": "healthy"
    }


@app.post("/upload")
async def upload(
        file: UploadFile = File(...)
):

    try:
        upload_file(
            file.file,
            file.filename
        )

        logger.info(
            f"Uploaded file {file.filename}"
        )

        put_metric("Uploads")

        return {
            "message": "File Uploaded"
        }
    except Exception as e:
        put_metric("Errors")
        logger.error(f"Upload failed: {str(e)}")
        raise


@app.get("/notify")
def notify():

    try:
        publish_message(
            "CloudLearn",
            "Test SNS Notification"
        )

        logger.info(
            "SNS Notification Sent"
        )

        put_metric("Notifications")

        return {
            "message": "SNS Sent"
        }
    except Exception as e:
        put_metric("Errors")
        logger.error(f"Notification failed: {str(e)}")
        raise


@app.get("/files")
def files():

    return {
        "files": list_files()
    }


@app.get("/view/{filename}")
def view_file(filename: str):

    obj = get_object(filename)

    return StreamingResponse(
        obj["Body"],
        media_type=obj["ContentType"]
    )


@app.get("/view-url/{filename}")
def view_url(filename: str):

    return {
        "url": generate_presigned_url(filename)
    }


@app.get("/log")
def log_test():

    logger.info(
        "CloudWatch Test Log"
    )

    return {
        "message": "Log Created"
    }