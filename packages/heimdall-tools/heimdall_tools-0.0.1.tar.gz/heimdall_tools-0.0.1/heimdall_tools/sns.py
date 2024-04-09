# This is an AWS SNS module. The processed MQTT messages will be sent to SNS topic by other services.
# There will be an different subscribers to SNS to queue/notify the messages for further processing.
# In the architecture, an HTTP endpoint shall read data from SQS for further processing in most of the cases.

import json
import boto3

def post_to_sns_topic(region, arn, key, value, topic):
    sns_client = boto3.client('sns', region_name = region)  # Replace 'your_region' with your AWS region

    message = {
        "key": key,
        "value" : value,
        "topic" : topic
    }
    json_data = json.dumps(message)
    # Publish the message to the SNS topic
    response = sns_client.publish(
        TopicArn = arn,
        Message = json_data
    )
    return response
