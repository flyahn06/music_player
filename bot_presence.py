import discord
import datetime
import logging
import asyncio

logging.basicConfig(format="%(asctime)s %(funcName)s : %(levelname)s : %(message)s",
                    level=logging.INFO)

app = discord.Client()
prev_music = ""

token = "NjEyMjYyNTE3MTU4MzEzOTg0.XVfz5w.ZdCmXctHkpE4kZDZtP7DpDN82G4"

@app.event
async def on_ready():
    print("다음으로 로그인합니다:\n    ID : {}\n    password : {}".format(app.user.name, app.user.id))
    print("=================")
    await app.change_presence(activity=discord.Game(name="대기", type=0), status=discord.Status.idle)
    return await update()

async def update():
    global prev_music

    while True:
        with open("musicInfo", "r") as f:
            current_music = f.readline()

        if not current_music == prev_music:
            if current_music == "stop":
                await app.change_presence(activity=discord.Game(name="대기"), status=discord.Status.idle)
            else:
                prev_music = current_music
                await app.change_presence(activity=discord.Game(name=f"{current_music} 을(를) 신나게 플레이", type=0), status=discord.Status.online)

        await asyncio.sleep(1)

app.run(token)
