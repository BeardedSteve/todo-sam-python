import json
from os import environ
from uuid import uuid4, UUID

import boto3
from bloop import Engine

from todoapi.models.todo import TodoItem

if environ.get("AWS_SAM_LOCAL") == "true":
    dynamodb = boto3.client('dynamodb', endpoint_url="http://dynamodb:8000")
    db = Engine(dynamodb=dynamodb)
    db.bind(TodoItem)

else:
    dynamodb = boto3.client('dynamodb')
    db = Engine(dynamodb=dynamodb)
    db.bind(TodoItem, skip_table_setup=True)


def get(event, context):
    #context.log(str(event))
    if event['pathParameters']:
        todo = db.query(TodoItem, key=TodoItem.uuid == UUID(event['pathParameters']['todo_id'])).one()
        body = todo.as_dict
    else:
        todos = db.scan(TodoItem)
        body = {"todos": [todo.as_dict for todo in todos]}
    return {"body": json.dumps(body), "statusCode": 200}


def put(event, context):
    context.log(str(event))
    todo = json.loads(event['body'])
    todo_item = TodoItem(
        uuid=todo.get("uuid", uuid4()),
        task=todo['task'],
        completed=todo.get("completed", False)
    )
    db.save(todo_item)
    return {"body": json.dumps({"todo": todo_item.as_dict}), "statusCode": 200}
