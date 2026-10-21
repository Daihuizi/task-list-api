from flask import abort, make_response
from ..db import db


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except (ValueError, TypeError):
        response = {"message": f"{cls.__name__} {model_id} invalid"}
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {"message": f"{cls.__name__} not found"}
        abort(make_response(response, 404))

    return model


def create_model(cls, request_body):
    if not isinstance(request_body, dict):
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    try:
        model = cls.from_dict(request_body)
    except (KeyError, TypeError, ValueError):
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(model)
    db.session.commit()

    return model.to_dict(), 201