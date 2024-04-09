import aiohttp
from disnake.ext import tasks
from loguru import logger

class SdcApi:
    def __init__(self):
        self.web_url = "https://api.server-discord.com/v2"
        self.session = aiohttp.ClientSession()

    @tasks.loop(minutes=30)
    async def post(self, bot_id: int = None, sdc_token=None, servers_count: int = None, shard_count: int = None):
        if not bot_id:
            raise ValueError("bot_id is required")
        if not sdc_token:
            raise ValueError("sdc_token is required")
        if not servers_count:
            raise ValueError("servers_count is required")
        if not shard_count:
            raise ValueError("shard_count is required")

        try:
            headers = {"Authorization": f"SDC {sdc_token}"}
            url = f"{self.web_url}/bots/{bot_id}/stats"
            payload = {"shards": shard_count, "servers": servers_count}
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status!= 200:
                    return print(await response.text())
                logger.success("SDC API: Статистика успешно отправлена следущее обновление статистики через 30 минут")
                return await response.json()
        except aiohttp.ClientError as e:
            return
