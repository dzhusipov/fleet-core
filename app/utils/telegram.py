"""Telegram Bot API notification sender."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramBot:
    """Send messages via Telegram Bot API."""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Send a message to a chat. Returns True on success."""
        if not self.base_url:
            logger.warning("Telegram bot not configured, skipping message to %s", chat_id)
            return False

        try:
            response = httpx.post(
                f"{self.base_url}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                timeout=10,
            )
            if response.status_code == 200:
                logger.info("Telegram message sent to %s", chat_id)
                return True
            else:
                logger.error("Telegram API error: %s", response.text)
                return False
        except Exception:
            logger.exception("Failed to send Telegram message to %s", chat_id)
            return False


telegram_bot = TelegramBot()
