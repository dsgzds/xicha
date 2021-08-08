from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
db = SQLAlchemy()

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    from app import db
    db.init_app(app)
    with app.test_request_context():
        db.create_all()
    from app.users.api import init_api
    init_api(app)
    # from resource.order import Order
    # Order.get()

    return app

def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContectTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(TaskBase, self).__call__(*args, **kwargs)

    celery.Task = ContectTask
    return celery