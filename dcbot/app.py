import discord
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

try:
    load_dotenv(dotenv_path='./.env.local')
except:
    load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # 你的 bot token
backend_url = os.getenv('BACKEND_URL') # 你的後端 url

class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        self.session = aiohttp.ClientSession()
        self.bg_task = self.loop.create_task(self.background_task())

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!set'):
            # 擷取訊息
            msg = message.content[len('!set'):].strip()
            print()
            # 傳送資訊到後端
            async with self.session.post(backend_url + '/brand', json={'brand': msg, 'channel_id': message.channel.channel_id}) as response:
                if response.status == 200:
                    await message.channel.send('已紀錄品牌名稱，當有新的策略時會通知您。')
                else:
                    await message.channel.send('紀錄品牌名稱失敗，請稍後再試。')

    async def background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            print('Checking new data...')
            async with self.session.get(backend_url + '/results') as response:
                data = await response.json()
                print(response.status, data)
                if response.status == 200 and data:
                    for item in data:
                        channel = self.get_channel(item['channel_id'])  # 你的頻道 ID
                        await channel.send(item['result'])
            await asyncio.sleep(500)  # 等待 5 秒

    async def close(self):
        await self.session.close()
        await super().close()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyBot(intents=intents)
client.run(TOKEN)
