import json
import logging

import boto3 as boto3

# Configure logging for AWS Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def send_to_q(data: str, q_url: str) -> dict:
    sqs = boto3.client('sqs')
    sqs_message = {
        'data': data,
    }

    logger.info("Sending to SQS in Utils: " + str(sqs_message))

    response = sqs.send_message(
        QueueUrl=q_url,
        MessageBody=json.dumps(sqs_message)
    )

    return response
