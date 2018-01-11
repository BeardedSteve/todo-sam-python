import json
from os import environ
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr

if environ.get("AWS_SAM_LOCAL") == "true":
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://dynamodb:8000")
    TABLE_NAME = "todos"
else:
    dynamodb = boto3.resource('dynamodb')
    TABLE_NAME = environ.get("TABLE_NAME", "todos")

table = dynamodb.Table(TABLE_NAME)


def get(event, context):
    context.log(str(event))
    try:
        todos = table.scan(
            FilterExpression=Attr('uuid').exists()
        )['Items']
    except Exception as err:
        context.log(str(err))
        todos = []
    body = {"todos": todos}
    return {"body": json.dumps(body), "statusCode": 200}


def put(event, context):
    context.log(str(event))
    todo = json.loads(event['body'])
    todo['uuid'] = uuid4().hex
    table.put_item(
        Item=todo
    )
    return {"body": json.dumps({"todo_id": todo['uuid']}), "statusCode": 200}
