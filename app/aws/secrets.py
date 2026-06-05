import boto3
import json

SECRET_NAME = "cloudlearn-app"

def get_secret():

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