import boto3
import sys
from Utils.constants import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def publish_custom_metric(namespace, metric_name, value):
    cloudwatch_client = boto3.client(
        'cloudwatch',
        region_name='us-east-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
    cloudwatch_client.put_metric_data(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': 'Count'
            },
        ]
    )


