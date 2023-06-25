import discord
import asyncio
import aiohttp
import os

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
            # 傳送資訊到後端
            async with self.session.post(backend_url + '/brand', json={'brand': msg, 'channel_id': message.channel.id}) as response:
                if response.status == 202:
                    await message.channel.send(f'已實時監控 **{msg}** ，當有新的策略時會通知您。')
                else:
                    await message.channel.send(f'監控 {msg} 失敗，請稍後再試。')

    async def background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            async with self.session.get(backend_url + '/results') as response:
                data = await response.json()
                if response.status == 200 and data:
                    for item in data:
                      channel = self.get_channel(item['channel_id'])
                      if channel:
                          await channel.send('監控到品牌，新策略如下：\n' + item['result'])

            await asyncio.sleep(30)  # 等待 30 秒

    async def close(self):
        await self.session.close()
        await super().close()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyBot(intents=intents)
client.run(TOKEN)
