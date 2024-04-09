from pathlib import Path
from typing import Callable

import httpx

from telegram_bot_reporter.core.base_bot import BaseBot


class Bot(BaseBot):
    def send_message(
        self,
        message: str,
        split_message: bool = False,
    ):
        """
        Send message to the Telegram chat.

        :param message: Text to send.
        :param split_message: If true, message will be sent by chunks.
            Defaults to False.
        :return: Response
        """

        if split_message:
            return self._send_chunks(message)
        return self._send_message(message)

    def send_document(
        self,
        file_path: Path | str,
        caption: str = "",
    ):
        """Send file as Telegram document.

        :param file_path: Path to the file.
        :param caption: Caption of the file. Defaults to empty string.
        :return: Response
        """

        with open(file_path, "rb") as f:
            data: dict = {
                "chat_id": self._chat_id,
                "caption": caption,
                "parse_mode": self._parse_mode,
            }
            return self._send_api_request(
                "sendDocument",
                headers={},
                data=data,
                files={"document": f},
            )

    def _send_chunks(self, message: str):
        for chunk in range(0, len(message), self._CHUNK):
            self._send_message(message[chunk : chunk + self._CHUNK])
        else:
            response = httpx.Response(status_code=200)

            return response

    def _send_message(self, message: str):
        if len(message) > self._CHUNK:
            raise ValueError(
                f"Message too long. Max length is {self._CHUNK} symbols."
            )

        data: dict = {
            "chat_id": self._chat_id,
            "text": f"{self._prefix}: {message}",
            "parse_mode": self._parse_mode,
        }
        return self._send_api_request(
            "sendMessage",
            json=data,
            headers=self._headers,
        )

    def _send_api_request(
        self,
        api_method: str,
        headers: dict,
        *_,
        **kwargs,
    ):
        transports: dict = {
            'httpx': self._send_using_httpx,
        }
        func: Callable = transports.get(self._transport)
        if not func:
            raise ValueError(f'Invalid transport type: {self._transport}')
        return func(
            api_method=api_method,
            headers=headers,
            **kwargs,
        )

    def _send_using_httpx(
        self,
        api_method: str,
        headers: dict,
        *_,
        **kwargs,
    ) -> httpx.Response:
        with httpx.Client() as session:
            response: httpx.Response = session.post(
                url=f"{self._url}/{api_method}",
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            )

            return response
