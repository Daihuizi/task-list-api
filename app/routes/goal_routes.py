from flask import Blueprint, request, Response
from app.models.goal import Goal
from app.models.task import Task
from app.db import db

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
def create_goal():
    # Get JSON data from the request
    request_body = request.get_json(silent=True)

    # Validate the required title field
    if not isinstance(request_body, dict) or "title" not in request_body:
        return {"details": "Invalid data"}, 400

    # Create a Goal object
    new_goal = Goal.from_dict(request_body)

    # Save the Goal to the database
    db.session.add(new_goal)
    db.session.commit()

    # Return the created Goal
    return new_goal.to_dict(), 201


@goals_bp.get("")
def get_goals():
    # Get all goals from the database
    goals = db.session.scalars(db.select(Goal)).all()

    # Convert each goal to a dictionary
    goals_response = [goal.to_dict() for goal in goals]

    # Return the list of goals
    return goals_response, 200


@goals_bp.get("/<goal_id>")
def get_goal(goal_id):
    # Validate the goal ID
    try:
        goal_id = int(goal_id)
    except ValueError:
        return {"message": "Invalid goal ID"}, 400

    # Find the goal in the database
    goal = db.session.get(Goal, goal_id)

    # Return 404 if the goal does not exist
    if goal is None:
        return {"message": "Goal not found"}, 404

    # Return the goal as JSON
    return goal.to_dict(), 200

@goals_bp.put("/<goal_id>")
def update_goal(goal_id):
    # Validate the goal ID
    try:
        goal_id = int(goal_id)
    except ValueError:
        return {"message": "Invalid goal ID"}, 400

    # Find the goal in the database
    goal = db.session.get(Goal, goal_id)

    # Return 404 if the goal does not exist
    if goal is None:
        return {"message": "Goal not found"}, 404

    # Get the request data
    request_body = request.get_json(silent=True)

    # Validate the required title field
    if not isinstance(request_body, dict) or "title" not in request_body:
        return {"details": "Invalid data"}, 400

    # Update the goal title
    goal.title = request_body["title"]
    db.session.commit()

    # Return 204 No Content
    return Response(status=204, mimetype="application/json")

@goals_bp.delete("/<goal_id>")
def delete_goal(goal_id):
    # Validate the goal ID
    try:
        goal_id = int(goal_id)
    except ValueError:
        return {"message": "Invalid goal ID"}, 400

    # Find the goal in the database
    goal = db.session.get(Goal, goal_id)

    # Return 404 if the goal does not exist
    if goal is None:
        return {"message": "Goal not found"}, 404

    # Delete the goal from the database
    db.session.delete(goal)
    db.session.commit()

    # Return 204 No Content
    return Response(status=204, mimetype="application/json")


@goals_bp.post("/<goal_id>/tasks")
def add_tasks_to_goal(goal_id):
    # Validate the goal ID
    try:
        goal_id = int(goal_id)
    except ValueError:
        return {"message": "Invalid goal ID"}, 400

    # Find the goal in the database
    goal = db.session.get(Goal, goal_id)

    # Return 404 if the goal does not exist
    if goal is None:
        return {"message": "Goal not found"}, 404

    # Get the request JSON
    request_body = request.get_json(silent=True)

    # Validate the task_ids field
    if not isinstance(request_body, dict) or not isinstance(request_body.get("task_ids"), list):
        return {"details": "Invalid data"}, 400

    task_ids = request_body["task_ids"]

    # Find each task and validate its ID
    tasks = []

    for task_id in task_ids:
        if type(task_id) is not int:
            return {"message": "Invalid task ID"}, 400

        task = db.session.get(Task, task_id)

        if task is None:
            return {"message": "Task not found"}, 404

        tasks.append(task)
     # Replace the goal's existing tasks with the new tasks
    goal.tasks = tasks

    # Save the relationship to the database
    db.session.commit()

    # Return the goal ID and associated task IDs
    return {
        "id": goal.id,
        "task_ids": [task.id for task in goal.tasks]
    }, 200



@goals_bp.get("/<goal_id>/tasks")
def get_tasks_for_goal(goal_id):
    # Validate the goal ID
    try:
        goal_id = int(goal_id)
    except ValueError:
        return {"message": "Invalid goal ID"}, 400

    # Find the goal in the database
    goal = db.session.get(Goal, goal_id)

    # Return 404 if the goal does not exist
    if goal is None:
        return {"message": "Goal not found"}, 404
    # Convert the goal to a dictionary
    response_body = goal.to_dict()

    # Add all associated tasks
    response_body["tasks"] = [task.to_dict() for task in goal.tasks]

    # Return the goal with its tasks
    return response_body, 200

    