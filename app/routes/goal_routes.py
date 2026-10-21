from flask import Blueprint, request, Response
from app.models.goal import Goal
from app.models.task import Task
from app.db import db
from app.routes.route_utilities import create_model, validate_model


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@goals_bp.post("")
def create_goal():
    request_body = request.get_json(silent=True)
    return create_model(Goal, request_body)


@goals_bp.get("")
def get_goals():
    goals = db.session.scalars(db.select(Goal)).all()

    goals_response = [goal.to_dict() for goal in goals]

    return goals_response, 200


@goals_bp.get("/<goal_id>")
def get_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    return goal.to_dict(), 200


@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json(silent=True)

    if not isinstance(request_body, dict) or "title" not in request_body:
        return {"details": "Invalid data"}, 400

    goal.title = request_body["title"]

    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    request_body = request.get_json(silent=True)

    if (
        not isinstance(request_body, dict)
        or not isinstance(request_body.get("task_ids"), list)
    ):
        return {"details": "Invalid data"}, 400

    task_ids = request_body["task_ids"]

    tasks = []

    for task_id in task_ids:
        if type(task_id) is not int:
            return {"message": "Invalid task ID"}, 400

        task = validate_model(Task, task_id)
        tasks.append(task)

    goal.tasks = tasks

    db.session.commit()

    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }, 200


@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    goal = validate_model(Goal, goal_id)

    response_body = goal.to_dict()

    response_body["tasks"] = [
        task.to_dict() for task in goal.tasks
    ]

    return response_body, 200