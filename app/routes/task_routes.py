import os
import requests

from flask import Blueprint, request, Response

from app.models.task import Task
from app.routes.route_utilities import (
    create_model,
    validate_model,
    get_models,
    update_model
)
from ..db import db


tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")


def notify_task_complete(task):
    url = os.environ.get("SLACK_API_URL")

    headers = {
        "Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }

    data = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {task.title}"
    }

    requests.post(url, headers=headers, json=data, timeout=10)


@tasks_bp.post("")
def create_task():
    request_body = request.get_json(silent=True)
    return create_model(Task, request_body)


@tasks_bp.get("")
def get_tasks():
    return get_models(Task)


@tasks_bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    return task.to_dict()


@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)

    request_body = request.get_json(silent=True)

    return update_model(
        task,
        request_body,
        ["title", "description"]
    )


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete(task_id):
    task = validate_model(Task, task_id)

    task.mark_complete()
    db.session.commit()

    notify_task_complete(task)

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")