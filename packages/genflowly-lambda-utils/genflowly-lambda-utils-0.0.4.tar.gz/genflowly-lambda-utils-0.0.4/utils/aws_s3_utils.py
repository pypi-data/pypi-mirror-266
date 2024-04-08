import boto3
import json


def read_from_s3(bucket_name, object_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)

    return json_content


def read_from_s3_in_dict(bucket_name, object_key):
    return read_from_s3(bucket_name, object_key)
