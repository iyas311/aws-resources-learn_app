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


def list_files():

    response = s3.list_objects_v2(
        Bucket=bucket
    )

    contents = response.get("Contents", [])

    return [item["Key"] for item in contents]


def get_object(filename):

    return s3.get_object(
        Bucket=bucket,
        Key=filename
    )


def delete_object(filename):

    return s3.delete_object(
        Bucket=bucket,
        Key=filename
    )


def generate_presigned_url(filename, expires_in=300):

    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket,
            "Key": filename
        },
        ExpiresIn=expires_in
    )