import boto3
import logging

from utils.contants import AWS_DEFAULT_REGION

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def save_to_dynamodb(table_name: str, data: dict, aws_region: str = AWS_DEFAULT_REGION) -> dict:
    logger.info("Received data object: %s", data)
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    response = {}
    try:
        table = dynamodb.Table(table_name)
        print("Received item_data : %s", data)
        response = table.put_item(Item=data)  # putItem expects a dict object
        logger.info("Saved data object: %s", str(response))
    except Exception as e:
        logger.error("Save to DynamoDB failed: %s", e)
    return response


def read_from_dynamodb(table_name: str, key: dict, aws_region: str = AWS_DEFAULT_REGION) -> dict:
    dynamodb = boto3.resource('dynamodb', region_name=aws_region)
    logger.error(dynamodb)
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)  # getItem expects a key
        if 'Item' in response:
            item = response['Item']
            logger.info("Retrieved item: %s", str(response['Item']))
            return {"status": 200, "response": item}
        else:
            logger.error("No item found with key: %s", key)
            return {"status": 404, "response": "No item found"}
    except Exception as e:
        logger.error("Read from DynamoDB failed: %s", e)
        return {"status": 500, "response": e}
