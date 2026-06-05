import boto3

from app.aws.secrets import get_secret

secret = get_secret()

bucket = secret["bucket_name"]

s3 = boto3.client(
    "s3",
    region_name="us-east-1"
)


def upload_file(file, filename):

    s3.upload_fileobj(
        file,
        bucket,
        filename
    )

    return filename