import os
import requests
from flask import Blueprint
from flask import Blueprint, request, make_response, abort, Response
from app.models.task import Task
from ..db import db
from flask import abort
from datetime import datetime

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try:
        new_task = Task.from_dict(request_body)
    except (KeyError, TypeError):
        return make_response({"details": "Invalid data"}, 400)

    db.session.add(new_task)
    db.session.commit()

    return make_response(new_task.to_dict(), 201)

@tasks_bp.get("")
def get_tasks():
   
    sort_order = request.args.get("sort")

   
    query = db.select(Task)

    
    if sort_order == "asc":
        query = query.order_by(Task.title.asc())

   
    elif sort_order == "desc":
        query = query.order_by(Task.title.desc())

    
    tasks = db.session.scalars(query).all()

    
    tasks_response = [task.to_dict() for task in tasks]

    return make_response(tasks_response, 200)

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_task(task_id)
    return make_response(task.to_dict(), 200)


def validate_task(task_id):
    try:
        task_id = int(task_id)
    except ValueError:
        abort(400, description="Invalid task ID")

    task = db.session.get(Task, task_id)

    if task is None:
        abort(404, description="Task not found")

    return task


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    # 1. Find the task or return 404
    task = validate_task(task_id)

    # 2. Update the completion time
    task.completed_at = datetime.now()
    db.session.commit()

    # 3. Prepare the Slack API request
    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }

    data = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }

    # 4. Send the Slack notification
    requests.post(url, headers=headers, json=data, timeout=10)

    # 5. Return 204 No Content
    return Response(status=204, mimetype="application/json")

@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    # 1. Find the task or return 404 if it does not exist
    task = validate_task(task_id)

    # 2. Reset the completion time to None
    task.completed_at = None

    # 3. Save the changes to the database
    db.session.commit()

    # 4. Return 204 No Content
    return Response(status=204, mimetype="application/json")