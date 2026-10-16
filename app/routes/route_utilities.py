from flask import abort
from ..db import db


def validate_model(model, model_id):
    # Check if the ID is a valid integer
    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        abort(400, description="Invalid ID")

    # Find the model instance in the database
    instance = db.session.get(model, model_id)

    # Return 404 if the instance does not exist
    if instance is None:
        abort(404, description="Not found")

    return instance

def create_model(model, request_body):
    # Validate the request body
    if not isinstance(request_body, dict):
        abort(400, description="Invalid data")

    # Create a model instance
    try:
        instance = model.from_dict(request_body)
    except (KeyError, TypeError, ValueError):
        abort(400, description="Invalid data")

    # Save the instance to the database
    db.session.add(instance)
    db.session.commit()

    # Return the created instance and status code
    return instance.to_dict(), 201