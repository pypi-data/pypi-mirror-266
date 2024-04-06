import logging

import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_state_machine_arn(state_machine_name: str) -> str:
    client = boto3.client('stepfunctions')

    # Get the list of all state machines
    state_machines = client.list_state_machines()['stateMachines']
    logging.info("List of from Step Functions:" + str(state_machines))

    # Find the state machine with the given name
    for sm in state_machines:
        if sm['name'] == state_machine_name:
            return sm['stateMachineArn']

    return ''


def start_step_functions(state_machine_arn: str, data_dict: dict):
    sfn = boto3.client('stepfunctions')
    response = sfn.start_execution(
        stateMachineArn=state_machine_arn,
        input=json.dumps(data_dict)
    )
    logging.info("Response from Step Functions Util:" + str(response))
    return response

