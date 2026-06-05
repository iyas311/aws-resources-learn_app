import boto3

from app.aws.secrets import get_secret

sns = boto3.client("sns")

topic = get_secret()["sns_topic_arn"]


def publish_message(subject, message):

    sns.publish(
        TopicArn=topic,
        Subject=subject,
        Message=message
    )