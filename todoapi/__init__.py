import json
from os import environ
from uuid import uuid4, UUID

import boto3
from bloop import Engine, ConstraintViolation

from todoapi.models.todo import TodoItem

if environ.get("AWS_SAM_LOCAL") == "true":
    dynamodb = boto3.client('dynamodb', endpoint_url="http://dynamodb:8000")
    db = Engine(dynamodb=dynamodb)
    db.bind(TodoItem)

else:
    dynamodb = boto3.client('dynamodb')
    db = Engine(dynamodb=dynamodb)
    db.bind(TodoItem, skip_table_setup=True)  # we can skip the table setup because CloudFormation will do it.


def get(event, context):
    if event['pathParameters']:
        todo_item = db.query(TodoItem, key=TodoItem.uuid == UUID(event['pathParameters']['todo_id'])).one()
        body = todo_item.as_dict
    else:
        todos = db.scan(TodoItem)
        body = {"todos": [todo_item.as_dict for todo_item in todos]}
    return {"body": json.dumps(body), "statusCode": 200}


def delete(event, context):
    todo_id = event['pathParameters']['todo_id']
    try:
        todo_item = db.query(TodoItem, key=TodoItem.uuid == UUID(todo_id)).one()
        db.delete(todo_item, atomic=True)
        return {"body": json.dumps({"message": f"{todo_item.uuid} deleted"}), "statusCode": 200}
    except ConstraintViolation as err:
        return {"body": json.dumps({"message": f"no todo with id {todo_uuid}"}), "statusCode": 404}


def put(event, context):
    if event['pathParameters']:
        todo_uuid = event['pathParameters']['todo_id']
        try:
            todo_item = db.query(TodoItem, key=TodoItem.uuid == UUID(todo_uuid)).one()
            todo_item.completed = True
            return {"body": json.dumps({"message": f"{todo_item.uuid} marked completed"}), "statusCode": 200}
        except ConstraintViolation as err:
            return {"body": json.dumps({"message": f"no todo with id {todo_uuid}"}), "statusCode": 404}

    else:
        todo = json.loads(event['body'])
        todo_item = TodoItem(
            uuid=todo.get("uuid", uuid4()),
            task=todo['task'],
            completed=todo.get("completed", False)
        )
        db.save(todo_item)
        return {"body": json.dumps({"todo": todo_item.as_dict}), "statusCode": 201}
