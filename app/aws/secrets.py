import boto3
import json

# Single secret name for all credentials
SECRET_NAME = "cloudlearn-app"

def get_secret():
    """
    Fetch all secrets from Secrets Manager.
    
    Contains:
    - S3 bucket_name
    - PostgreSQL credentials (username, password, host, port, database)
    
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