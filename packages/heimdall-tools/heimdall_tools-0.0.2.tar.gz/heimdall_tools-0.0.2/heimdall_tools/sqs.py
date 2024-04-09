# This is an AWS SQS module. The processed messages will be sent to SNS topic by other services.
# SQS queue subscribe to this SNS topic to queue the messages for further processing.
# In the architecture, an HTTP endpoint shall read data from SQS for further processing in most of the cases.

import json
import boto3

def read_from_sqs_queue(region, queue_url, max_number_messages = 10, timeout_secs = 20, delete_on_read = True):
    sqs_client = boto3.client('sqs', region_name = region)  # Replace 'your_region' with your AWS region

    # Receive messages from the queue
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages = max_number_messages,  # Maximum number of messages to retrieve
        WaitTimeSeconds = timeout_secs,      # Long polling: Wait up to 20 seconds for messages
    )

    if True == delete_on_read:
        if 'Messages' in response:
            # Process each message
            for message in response['Messages']:
                # Delete the message from the queue
                sqs_client.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )

    return response