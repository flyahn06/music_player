import discord
from discord.ext import commands
import glob
import datetime

token = "private"

bot = commands.Bot("~")

music_list = glob.glob("music/*.mp3")
artist_title = {}
titles = []
artists = []
print(music_list)

queue = []

for music in music_list:
    # 곡의 형식: location/artist - title
    fullname = music.split('/')[1].strip()
    title = fullname.split('-')[0].strip()
    artist = fullname.split('-')[1].replace(".mp3", "").strip()

    artist_title[title] = artist
    titles.append(music.replace("music/", "").replace(".mp3", ""))

print(artist_title)
title_artist = {v: k for k, v in artist_title.items()}
print(title_artist)
print(titles)

# == 음악 목록 함수 ==

@bot.command(name="list")
async def _list(ctx):
    embed=discord.Embed(title="재생 가능한 음악 목록", description="/music 에 있는 음악 목록", color=0x2215e0)
    for title, artist in artist_title.items():
        embed.add_field(name=artist, value=title, inline=False)
    embed.set_footer(text=f"{datetime.datetime.now()} 에 {ctx.author.name}님이 요청")
    await ctx.send(embed=embed)


# == 음성 채널 참가 및 나가기 관련 함수 ==

# 음성 채널 참가 명령
@bot.command(name = "join")
async def _join(ctx):
    channel = ctx.author.voice.channel
    
    await channel.connect()
    await ctx.send(":white_check_mark: 음성 채널에 참가하였습니다.")

# 음성채널 참가 예외 헨들러
@_join.error
async def _join_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send(":x: {} 아무래도 현재 음성 채널에 참가하지 않으신 것 같네요. 참가한 후 다시 !join 을 사용해 주세요.".format(ctx.author.mention))

# 음성 채널 나가기
@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send(":hand_splayed: 음성 채널에서 나갔습니다. 나중에 보자구요.")

# == 큐 관련 함수 ==

# 큐에 음악 추가
@bot.command()
async def add(ctx, *name):
    global queue

    name = " ".join(name)

    print(name)

    if name in titles:
        await ctx.send(":pushpin: 음악 {} 을(를) 큐에 추가했습니다.".format(name))
        queue.append(name)
    else:
        await ctx.send(":cry: {} 그 음악은 없는 것 같네요.".format(ctx.author.mention))

# ctx 없는 비동기형 코루틴 (큐 음악 추가)
async def nonctxadd(ctx, name):
    global queue

    if name in titles:
        await ctx.send(":pushpin: 음악 {} 을(를) 큐에 추가했습니다.".format(name))
        queue.append(name)
        return True
    else:
        await ctx.send(":cry: {} 그 음악은 없는 것 같네요.".format(ctx.author.mention))
        return False

# 큐 출력
@bot.command(name="queue", aliases=['큐', '재생목록'])
async def _queue(ctx):
    embed=discord.Embed(title="큐에 있는 음악 목록", color=0x2215e0)
    for item, i in zip(queue, range(1, len(queue)+1)):
        embed.add_field(name=i, value=item, inline=False)
    embed.set_footer(text=f"{datetime.datetime.now()} 에 {ctx.author.name}님이 요청")
    await ctx.send(embed=embed)

# 큐 비우기
@bot.command()
async def clearqueue(ctx):
    global queue
    queue.clear()
    await ctx.send(":white_check_mark: 큐를 초기화 했습니다.")

# == 음악 재생 함수 ==

# main: 얼라이어스 p: 음악 추가
@bot.command(aliases=['p'])
async def play(ctx, *names):
    global queue

    if names:
        name = " ".join(names)
        if not await nonctxadd(ctx, name):
            return
    elif queue:
        queue.reverse()
        name = queue.pop()
        queue.reverse()
    else:
        await ctx.send(":x: 큐에 음악이 아무것도 없는 듯 합니다. 음악을 추가하거나 음악 제목을 입력해 주새요!")
        return

    try:
        ctx.voice_client.play(discord.FFmpegPCMAudio("music/{}.mp3".format(name)))
    except discord.ClientException:
        await ctx.send(":x: 이미 다른 음악이 플레이 중인 것 같아요. !add 명령을 사용해서 큐에 음악을 추가해 주세요!")
    except FileNotFoundError:
        await ctx.send(":x: 아직 그 음악은 없는 것 같아요. !request 명령을 이용해서 음악을 추가해 주세요!")
    else:
        await ctx.send(":loudspeaker: {} 을(를) 플레이합니다. 귀를 기울여 주세요!".format(name))

# == 음악 컨트롤 함수 ==

# 음악 일시정지
@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()
    await ctx.send(":white_check_mark: 현재 재생 중인 음악을 일시정지했습니다. !resume 명령을 사용해서 이어 들으실 수 있어요!")

# 음악 다시 재생
@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()
    await ctx.send(":white_check_mark: 방금까지 듣던 음악을 다시 재생했어요!")

# 음악 정지
@bot.command()
async def stop(ctx):
    ctx.voice_client.stop()
    await ctx.send(":white_check_mark: 음악을 정지했어요.")

@bot.command()
async def skip(ctx):
    await ctx.send(":point_right: 방금까지 듣던 음악을 스킵했어요! 잠시 후에 큐에 있는 다음 음악이 재생될 거에요.")
    return await play(ctx)


@bot.command(name="del")
async def _del(ctx, amount):
    await ctx.channel.purge(limit=int(amount)+1)

bot.run(token)
