import aiohttp
import asyncio
import logging
from .interval import Global

class SdcApi:
    def __init__(self, logger=None, interval=30):
        self.web_url = "https://api.server-discord.com/v2"
        self.session = aiohttp.ClientSession()
        self.logger = logger or logging.getLogger(__name__)
        self.interval = interval
        Global.interval = interval

    async def post_stats_loop(self, bot_id, sdc_token, servers_count, shard_count):
        while True:
            await self.post_stats(bot_id, sdc_token, servers_count, shard_count)
            await asyncio.sleep(self.interval * 60)

    async def post_stats(self, bot_id: int, sdc_token: str, servers_count: int, shard_count: int = 1):
        if not isinstance(bot_id, int):
            raise ValueError("bot_id must be an integer")
        if not isinstance(sdc_token, str):
            raise ValueError("sdc_token must be a string")
        if not isinstance(servers_count, int):
            raise ValueError("servers_count must be an integer")
        if not isinstance(shard_count, int):
            raise ValueError("shard_count must be an integer")

        try:
            headers = {"Authorization": f"SDC {sdc_token}"}
            url = f"{self.web_url}/bots/{bot_id}/stats"
            payload = {"shards": shard_count, "servers": servers_count}
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    self.logger.error("Failed to send statistics to SDC API: %s", await response.text())
                else:
                    self.logger.success("Statistics successfully sent to SDC API. Next update in %s minutes", self.interval)
        except aiohttp.ClientError as e:
            self.logger.exception("Error while sending statistics to SDC API")

    async def start_posting_stats(self, bot_id, sdc_token, servers_count, shard_count=1):
        asyncio.create_task(self.post_stats_loop(bot_id, sdc_token, servers_count, shard_count))
