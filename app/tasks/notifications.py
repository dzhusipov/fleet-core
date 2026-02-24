"""Celery tasks for sending email and Telegram notifications."""

from app.tasks.celery_app import celery_app
from app.utils.email import email_sender
from app.utils.telegram import telegram_bot


@celery_app.task
def send_email_notification(to: str, subject: str, body_html: str):
    """Send an email notification asynchronously."""
    return email_sender.send(to, subject, body_html)


@celery_app.task
def send_telegram_notification(chat_id: str, text: str):
    """Send a Telegram notification asynchronously."""
    return telegram_bot.send_message(chat_id, text)
