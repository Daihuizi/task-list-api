import os
import requests
from datetime import datetime
from flask import Blueprint, request, make_response, Response
from app.models.task import Task
from app.routes.route_utilities import create_model, validate_model
from ..db import db


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


@tasks_bp.post("")
def create_task():
    request_body = request.get_json(silent=True)
    return create_model(Task, request_body)


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
    task = validate_model(Task, task_id)
    return make_response(task.to_dict(), 200)


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    url = "https://slack.com/api/chat.postMessage"

    headers = {
        "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }

    data = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }

    requests.post(url, headers=headers, json=data, timeout=10)

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")