import logging
import watchtower
import boto3

logs_client = boto3.client(
    "logs",
    region_name="us-east-1"
)

logger = logging.getLogger("cloudlearn")

logger.setLevel(logging.INFO)

logger.addHandler(
    watchtower.CloudWatchLogHandler(
        boto3_client=logs_client,
        log_group_name="/cloudlearn/application"
    )
)