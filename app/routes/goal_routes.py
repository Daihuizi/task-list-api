from flask import Blueprint, request, Response
from werkzeug.exceptions import HTTPException

from app.models.goal import Goal
from app.models.task import Task
from app.db import db
from app.routes.route_utilities import create_model, validate_model


goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


# --------------------------------------------------
# Shared Goal Validation
# --------------------------------------------------

def validate_goal(goal_id):
    # Validate and retrieve a Goal using the shared utility
    try:
        return validate_model(Goal, goal_id)

    # Preserve the existing JSON error responses
    except HTTPException as error:
        if error.code == 400:
            return {"message": "Invalid goal ID"}, 400

        if error.code == 404:
            return {"message": "Goal not found"}, 404

        raise


# --------------------------------------------------
# Create Goal
# --------------------------------------------------

@goals_bp.post("")
def create_goal():
    # Get the request data
    request_body = request.get_json(silent=True)

    # Create the goal using the shared utility
    try:
        return create_model(Goal, request_body)

    except HTTPException as error:
        if error.code == 400:
            return {"details": "Invalid data"}, 400

        raise


# --------------------------------------------------
# Get All Goals
# --------------------------------------------------

@goals_bp.get("")
def get_goals():
    # Retrieve all goals from the database
    goals = db.session.scalars(db.select(Goal)).all()

    # Convert each goal to a dictionary
    goals_response = [goal.to_dict() for goal in goals]

    return goals_response, 200


# --------------------------------------------------
# Get One Goal
# --------------------------------------------------

@goals_bp.get("/<goal_id>")
def get_goal(goal_id):
    # Validate and retrieve the goal
    result = validate_goal(goal_id)

    # Return the existing error response if validation failed
    if isinstance(result, tuple):
        return result

    goal = result

    return goal.to_dict(), 200


# --------------------------------------------------
# Update Goal
# --------------------------------------------------

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    # Validate and retrieve the goal
    result = validate_goal(goal_id)

    if isinstance(result, tuple):
        return result

    goal = result

    # Get the request data
    request_body = request.get_json(silent=True)

    # Validate the required title field
    if not isinstance(request_body, dict) or "title" not in request_body:
        return {"details": "Invalid data"}, 400

    # Update the goal title
    goal.title = request_body["title"]

    # Save changes to the database
    db.session.commit()

    return Response(status=204, mimetype="application/json")


# --------------------------------------------------
# Delete Goal
# --------------------------------------------------

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    # Validate and retrieve the goal
    result = validate_goal(goal_id)

    if isinstance(result, tuple):
        return result

    goal = result

    # Delete the goal from the database
    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


# --------------------------------------------------
# Add Tasks to Goal
# --------------------------------------------------

@goals_bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    # Validate and retrieve the goal
    result = validate_goal(goal_id)

    if isinstance(result, tuple):
        return result

    goal = result

    # Get the request data
    request_body = request.get_json(silent=True)

    # Validate the task_ids field
    if (
        not isinstance(request_body, dict)
        or not isinstance(request_body.get("task_ids"), list)
    ):
        return {"details": "Invalid data"}, 400

    task_ids = request_body["task_ids"]

    # Find and validate each task
    tasks = []

    for task_id in task_ids:
        if type(task_id) is not int:
            return {"message": "Invalid task ID"}, 400

        try:
            task = validate_model(Task, task_id)

        except HTTPException as error:
            if error.code == 400:
                return {"message": "Invalid task ID"}, 400

            if error.code == 404:
                return {"message": "Task not found"}, 404

            raise

        tasks.append(task)

    # Replace existing task associations
    goal.tasks = tasks

    # Save the relationship changes
    db.session.commit()

    # Return the goal ID and associated task IDs
    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }, 200


# --------------------------------------------------
# Get Tasks for Goal
# --------------------------------------------------

@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    # Validate and retrieve the goal
    result = validate_goal(goal_id)

    if isinstance(result, tuple):
        return result

    goal = result

    # Convert the goal to a dictionary
    response_body = goal.to_dict()

    # Add all associated tasks
    response_body["tasks"] = [
        task.to_dict() for task in goal.tasks
    ]

    return response_body, 200