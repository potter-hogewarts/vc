import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import ffmpeg
from voice_generator import creat_WAV
from datetime import datetime, timedelta, timezone
#from pytz import timezone
import time


intents=discord.Intents.all()
client = commands.Bot(command_prefix='.',intents=intents)
voice_client = None
#チャンネルの発言権
channel_id = 0

#カズマサを使用している場合は1を使用していない場合は0を
channel_ctx = 0

@client.event
async def on_ready():
    global channel
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name="🎣釣り"))


@client.command()
async def join(ctx):
    global channel_ctx
    global channel_id
    #global mem_len
    #print(channel_ctx)

    #どこかのVCチャンネルで使われていない場合使えるようにする
    if channel_ctx == 0:
        print('#join')
        print('#voicechannelを取得')
        try:
            vc = ctx.author.voice.channel
            print('#voicechannelに接続')
            await vc.connect()
            channel_id = ctx.message.channel.id
            channel_ctx = 1
            await ctx.send('邪魔するぜ！あるじ')
            embed = discord.Embed(title="聞き専ボット(カズマサ)の使い方",description="※注意:ワシが他のVCに入ってるときは使えねぇから容赦してくれ！",color=discord.Colour.green())
            embed.add_field(name="`.join`",value="ワシがVCに参加されるぜ！",inline=False)
            embed.add_field(name="`.bye`",value="ワシがVCから抜けるぜ！",inline=False)
            embed.add_field(name="`.register` `単語` `読み方`",value="ワシに発音してほしい単語と読み方をセットしてくれ！",inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("ワシで遊ぶな(｀´）")
            pass

    elif channel_ctx == 1:
        await ctx.send("すまん、使用中だ(;_:)")

@client.command()
async def bye(ctx):
    global channel_ctx
    global channel_id
    print('#bye')
    print('#切断')
    await ctx.send('失礼するぜ!あるじ')
    await ctx.voice_client.disconnect()
    channel_ctx = 0
    channel_id = 0

@client.command()
async def register(ctx, arg1, arg2):
    with open('dic.txt', encoding='CP932', mode='a') as f:
        f.write('\n'+ arg1 + ',' + arg2)
        print('dic.txtに書き込み：''\n'+ arg1 + ',' + arg2)
    await ctx.send('`' + arg1+'` を `'+arg2+'` として登録したぜ!')

@client.command()
async def kazumasa(ctx):
    #global channel_id
    #channel_id = ctx.message.channel.id
    embed = discord.Embed(title="聞き専ボット(カズマサ)の使い方",description="※注意:ワシが他のVCに入ってるときは使えねぇから容赦してくれ！",color=discord.Colour.green())
    embed.add_field(name="`.kazumasa`",value="ワシの使い方一覧が表示されるぜ！")
    embed.add_field(name="`.join`",value="ワシがVCに参加されるぜ！",inline=False)
    embed.add_field(name="`.bye`",value="ワシがVCから抜けるぜ！",inline=False)
    embed.add_field(name="`.register` `単語` `読み方`",value="ワシに発音してほしい単語と読み方をセットしてくれ！",inline=False)
    await ctx.send(embed=embed)

@client.event
async def on_voice_state_update(member, before, after):
    global channel_ctx
    global channel_id

    #VCから人が抜けて人の人数がゼロの時
    if after.channel is None:
        channel_ctx = 0
        channel_id = 0
        mem_len_bfr = len(before.channel.members)

        #VCにカズマサのみの時切断する
        if (mem_len_bfr - 1) == 0:
            try:
                await member.guild.voice_client.disconnect()
            except:
                pass


@client.listen("on_message")
async def msg(message):
    global channel_id

    if message.channel.id == channel_id:
        print('---on_message_start---')
        msgclient = message.guild.voice_client
        print(msgclient)
        if message.content.startswith('.'):
            pass

        else:
    
            if message.channel.id == channel_id:
                if message.guild.voice_client:
                    print('#message.content:'+ message.content)
                    creat_WAV(message.content)
                    #source = discord.FFmpegPCMAudio(executable="C:\\open_jtalk\\bin\\ffmpeg-N-102572-gf27e3ccf06-win64-gpl-shared\\bin\\ffmpeg.exe",source="output.wav")
                    #source = discord.FFmpegPCMAudio(source="output.wav",executable="C:\\open_jtalk\\bin\\ffmpeg-N-102572-gf27e3ccf06-win64-gpl-shared\\bin\\ffmpeg.exe")
                    #debian(heroku)
                    source = discord.FFmpegPCMAudio(source="output.wav",executable="./bin/ffmpeg")
                    #windows10
                    #source = discord.FFmpegPCMAudio(source="output.wav",executable="./bin/ffmpeg.exe")
                    message.guild.voice_client.play(source)
                else:
                    pass
        await client.process_commands(message)

        print('---on_message_end---')

#ご自身のディスコードボットのトークンIDをつけてください
client.run("TOKEN_ID")