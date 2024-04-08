import boto3
from botocore.exceptions import ClientError
import base64

def get_secret(secret_arn: str) -> str:
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_arn
        )
    except ClientError as e:
        raise Exception("Couldn't retrieve the secret.") from e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return secret
