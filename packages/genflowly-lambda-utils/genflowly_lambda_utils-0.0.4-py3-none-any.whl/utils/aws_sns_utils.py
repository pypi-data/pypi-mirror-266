import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def publish_to_sns(topic_arn: str, message: dict) -> dict:
    logger.info("Received object to send to SNS Util %s", message)
    logger.info("Received topic ARN to send to SNS Util %s", topic_arn)
    try:
        sns = boto3.client('sns')
        sns_response = sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message),
            MessageStructure='json'
        )
        logger.info("SNS response: " + str(sns_response))
        return sns_response
    except Exception as e:
        logger.exception("Error in sending notification to SNS")
        raise
