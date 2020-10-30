from celery import Celery

app = Celery(
    'simpli',
    backend='redis://localhost:6379/0',
    broker=''
)