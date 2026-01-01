import aiohttp
import structlog

logger = structlog.get_logger()


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str) -> None:
        self._token = token
        self._chat_id = chat_id

    async def send(self, message: str) -> None:
        """
        Send a message via Telegram bot.

        Args:
            message: Message text to send

        Raises:
            Exception: If message fails to send
        """
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {"chat_id": self._chat_id, "text": message}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    data = await response.json()

                    if response.status == 200 and data.get("ok"):
                        logger.info(
                            "telegram.message.sent",
                            message_id=data.get("result", {}).get("message_id"),
                        )
                    else:
                        logger.error(
                            "telegram.message.failed",
                            status=response.status,
                            error=data.get("description", "Unknown error"),
                        )
                        raise Exception(f"Telegram API error: {data.get('description')}")

            except aiohttp.ClientError as exc:
                logger.error("telegram.connection.failed", error=str(exc))
                raise
            except Exception as exc:
                logger.error("telegram.send.error", error=str(exc))
                raise
