from celery import Celery
import random
import time

# app = Celery('celery_config', backend='redis://localhost',broker='redis://localhost:6379/0', include=['tasks', 'celery_add'])

def make_celery(app):
    # celery = Celery('celery_config',
    #                 backend='redis://localhost',
    #                 broker='redis://localhost:6379/0', include=['tasks', 'celery_add'])
    celery = Celery(app.import_name,
                    backend = app.config['CELERY_BACKEND'],
                    broker = app.config['CELERY_BROKER_URL'],
                    # include=['tasks', 'celery_add'])
                    include=[ 'celery_add'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery