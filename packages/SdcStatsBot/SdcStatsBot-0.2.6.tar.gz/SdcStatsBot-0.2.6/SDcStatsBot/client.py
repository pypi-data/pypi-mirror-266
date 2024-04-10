import aiohttp
import asyncio

class SdcApi:
    def __init__(self, logger=None, interval=30):
        if not isinstance(interval, int):
            raise ValueError("interval must be an integer")
        if interval < 30:
            raise ValueError("interval must be a positive integer")

        self.web_url = "https://api.server-discord.com/v2"
        self.session = aiohttp.ClientSession()
        self.interval = interval

    async def post_stats_loop(self, bot_id: int, sdc_token: str, servers_count: int, shard_count: int):
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
                data = await response.json()
                try:
                    error = data['error']
                except:
                    error = None
                if not error:
                    return print("Statistics successfully sent to SDC API. Next update in %s minutes", self.interval)
                print("Failed to send statistics to SDC API: %s", data['error']['message'])
        except aiohttp.ClientError as e:
            print("Error while sending statistics to SDC API")

    async def start_posting_stats(self, bot_id: int, sdc_token: str, servers_count: int, shard_count: int = 1):
        asyncio.create_task(self.post_stats_loop(bot_id, sdc_token, servers_count, shard_count))
