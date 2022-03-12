import random
import typing
from typing import Optional

from app.web.utils import sjson_dumps

from aiohttp import TCPConnector
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Update, Message, UpdateObject
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=TCPConnector(verify_ssl=False))
        try:
            await self._get_long_poll_service()
        except Exception as e:
            self.logger.error("Exception", exc_info=e)
        self.poller = Poller(app.store)
        self.logger.info("start polling")
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "group_id": self.app.config.bot.group_id,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as resp:
            data = (await resp.json())["response"]
            self.logger.info(data)
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]
            self.logger.info(self.server)

    async def poll(self) -> list[Update]:
        new_url = self._build_query(
                host=self.server,
                method="",
                params={
                    "act": "a_check",
                    "key": self.key,
                    "ts": self.ts,
                    "wait": 5,
                },
            )
        async with self.session.get(new_url) as resp:
            data = await resp.json()
            self.logger.info(data)
            if "failed" in data.keys():
                await self._get_long_poll_service()
                return []
            else:
                self.ts = data["ts"]
                raw_updates = data.get("updates", [])
                updates = []
                for update in raw_updates:
                    updates.append(Update.from_dict(update)) 
            return updates

    async def send_message(self, message: Message, params = None, keyboard=None) -> None:
        
        if params is None:
            params={
                        #"user_id": None if message.peer_id else message.user_id,
                        "random_id": random.randint(1, 2 ** 32),
                        "peer_id": message.peer_id,
                        "message": message.text,
                        "access_token": self.app.config.bot.token,
                    }
        if keyboard is not None:
            params["keyboard"] = sjson_dumps(keyboard)
        async with self.session.post(
            self._build_query(
                API_PATH,
                "messages.send",
                params,
            )
        ) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def send_snackbar(self, params: dict = None, event_data: dict = None):
        params["event_data"] = sjson_dumps(event_data)
        params["access_token"] = self.app.config.bot.token
        async with self.session.post(
            self._build_query(API_PATH, "messages.sendMessageEventAnswer", params)) as resp:
            data = await resp.json()
            self.logger.info(data)

    async def get_username(self, vk_id: int) -> str:
        params = {"user_ids": vk_id,
                  "access_token": self.app.config.bot.token,}
        
        async with self.session.get(
            self._build_query(API_PATH, "users.get", params,)) as resp:
            data = await resp.json()
            self.logger.info(data)
        username = data["response"][0]["first_name"] + " " + data["response"][0]["last_name"]
        return username


        
