
from flask import abort, make_response, request
from ..db import db


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
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
    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    db.session.add(model)
    db.session.commit()

    return model.to_dict(), 201


def get_models(cls):
    sort_order = request.args.get("sort")

    query = db.select(cls)

    if sort_order == "asc":
        query = query.order_by(cls.title.asc())
    elif sort_order == "desc":
        query = query.order_by(cls.title.desc())

    models = db.session.scalars(query).all()
    models_response = [model.to_dict() for model in models]

    return models_response


def update_model(model, request_body, required_fields):
    if not isinstance(request_body, dict):
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))

    for field in required_fields:
        if field not in request_body:
            response = {"details": "Invalid data"}
            abort(make_response(response, 400))

    for field in required_fields:
        setattr(model, field, request_body[field])

    db.session.commit()

    return make_response("", 204, {"Content-Type": "application/json"})
