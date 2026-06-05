import boto3
import json

# Single secret name for all credentials
SECRET_NAME = "cloudlearn-app"

def get_secret():
    """
    Fetch all secrets from Secrets Manager.

    Contains:
    - S3 bucket_name
    - SNS topic ARN
    - PostgreSQL credentials (db_username, db_password, db_host, db_port, db_name)

    Returns:
        Dictionary with all secret values
    """
    client = boto3.client(
        "secretsmanager",
        region_name="us-east-1"
    )

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    return json.loads(
        response["SecretString"]
    )
