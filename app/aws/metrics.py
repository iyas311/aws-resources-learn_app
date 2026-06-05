import boto3

cloudwatch = boto3.client(
    "cloudwatch",
    region_name="us-east-1"
)


def put_metric(metric_name, value=1):

    cloudwatch.put_metric_data(
        Namespace="CloudLearn",
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value
            }
        ]
    )