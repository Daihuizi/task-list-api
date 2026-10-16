from flask import Blueprint, request, Response
from app.models.goal import Goal
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