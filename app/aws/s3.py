import boto3

from app.aws.secrets import get_secret

secret = get_secret()

bucket = secret["bucket_name"]

s3 = boto3.client(
    "s3",
    region_name="us-east-1"
)