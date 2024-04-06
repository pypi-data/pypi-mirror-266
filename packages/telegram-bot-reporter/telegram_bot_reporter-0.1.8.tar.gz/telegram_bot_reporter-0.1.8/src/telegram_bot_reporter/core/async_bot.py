from pathlib import Path

import niquests

from telegram_bot_reporter.core.base_bot import BaseBot


class AsyncBot(BaseBot):
    async def send_message(
        self,
        message: str,
        split_message: bool = False,
    ) -> niquests.Response:
        """
        Send message to the Telegram chat.

        :param message: Text to send.
        :param split_message: If true, message will be sent by chunks.
            Defaults to False.
        :return: niquests.Response

        """

        if split_message:
            return await self._send_chunks(message)
        return await self._send_message(message)

    async def send_document(
        self,
        file_path: Path | str,
        caption: str = "",
    ) -> niquests.Response:
        """Send file as Telegram document.

        :param file_path: Path to the file.
        :param caption: Caption of the file. Defaults to empty string.
        :return: niquests.Response
        """

        with open(file_path, "rb") as f:
            data: dict = {
                "chat_id": self._chat_id,
                "caption": caption,
                "parse_mode": self._parse_mode,
            }
            return await self._send_api_request(
                "sendDocument",
                headers={},
                data=data,
                files={"document": f},
            )

    async def _send_chunks(self, message: str) -> niquests.Response:
        for chunk in range(0, len(message), self._CHUNK):
            await self._send_message(message[chunk : chunk + self._CHUNK])
        else:
            response = niquests.Response()
            response.status_code = 200

            return response

    async def _send_message(self, message: str) -> niquests.Response:
        if len(message) > self._CHUNK:
            raise ValueError(
                f"Message too long. Max length is {self._CHUNK} symbols."
            )

        data: dict = {
            "chat_id": self._chat_id,
            "text": f"{self._prefix}: {message}",
            "parse_mode": self._parse_mode,
        }
        return await self._send_api_request(
            "sendMessage",
            json=data,
            headers=self._headers,
        )

    async def _send_api_request(
        self,
        api_method: str,
        headers: dict,
        *_,
        **kwargs,
    ) -> niquests.Response:
        async with niquests.AsyncSession() as session:
            response: niquests.Response = await session.post(
                url=f"{self._url}/{api_method}",
                headers=headers,
                timeout=self._timeout,
                **kwargs,
            )

            return response
