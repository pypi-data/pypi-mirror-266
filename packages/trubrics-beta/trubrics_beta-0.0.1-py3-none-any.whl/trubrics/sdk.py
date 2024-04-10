import asyncio
import json
import threading
import uuid
from pathlib import Path

import aiohttp
import requests


class Trubrics:
    def __init__(
        self, api_key: str, host: str = "https://ingestion-k65vkv2tua-ew.a.run.app"
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.host = host

    async def post_event(
        self, session, event, role, session_id, role_id=None, properties=None
    ):
        role_id = role_id or str(uuid.uuid4())
        try:
            post_request = session.post(
                Path(self.host) / "publish_event",
                params={"project_api_key": self.api_key},
                headers={"Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "event": event,
                        "role": role,
                        "role_id": role_id,
                        "session_id": session_id,
                        "properties": properties,
                    }
                ),
            )
            async with post_request as response:
                response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Error posting event: {e}")

    @staticmethod
    def run_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def track(self, event, role, session_id, role_id=None, properties=None):
        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.run_asyncio_loop, args=(new_loop,))
        t.start()

        async def async_task():
            async with aiohttp.ClientSession() as session:
                await self.post_event(
                    session, event, role, session_id, role_id, properties
                )

        asyncio.run_coroutine_threadsafe(async_task(), new_loop)

    def track_sync(self, event, role, session_id, role_id=None, properties=None):
        with requests.Session() as session:
            role_id = role_id or str(uuid.uuid4())
            try:
                post_request = session.post(
                    Path(self.host) / "publish_event",
                    params={"project_api_key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(
                        {
                            "event": event,
                            "role": role,
                            "role_id": role_id,
                            "session_id": session_id,
                            "properties": properties,
                        }
                    ),
                )
                post_request.raise_for_status()
            except Exception as e:
                raise ValueError(f"Error posting event: {e}")
