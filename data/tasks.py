from celery import shared_task
from .db_loader import DBLoader

@shared_task
def update_db():
    DBLoader().update_db()
