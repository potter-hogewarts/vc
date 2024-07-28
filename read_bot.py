import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import ffmpeg
from voice_generator import creat_WAV
from voice_generator import mod_pitch
from voice_generator import mod_speed
from datetime import datetime, timedelta, timezone
#from pytz import timezone
import time
import random
import json
import mojimoji


TOKEN = os.getenv('TOKEN')
intents=discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

voice_client = None
channel = None
#チャンネルの発言権
channel_id = 0
mem_id = None

#カズマサを使用している場合は1を使用していない場合は0を
channel_ctx = 0


class HogeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HugaButton("読み上げボットを呼ぶ"))
        self.add_item(HugaButton("読み上げボットを呼ばない"))
        self.message = None
    
    #エラーが起きたらボタンを削除する
    async def on_error(interaction,error,item):
        global channel_ctx
        channel_ctx = 0

        print("------------error------------")
        print(error)
        print("-----------------------------")
        await interaction.response.send_message("すまんが何か不具合が起きたみたいだ！もう一回やってくれ")
        await interaction.message.delete()


class HugaButton(discord.ui.Button):
    def __init__(self,txt:str):
        super().__init__(label=txt,style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        global channel_ctx
        global mem_id

        if self.label == "読み上げボットを呼ぶ":
            channel_ctx = 1
            mem_id = interaction.user.id
            await interaction.response.send_message("邪魔するぜ！")
            vc=interaction.user.voice.channel
            await vc.connect(timeout=50,reconnect=True)
            await interaction.message.delete()
            return

        if self.label == "読み上げボットを呼ばない":
            channel_ctx = 0
            await interaction.message.delete()
            return



@client.event
async def on_ready():
    global channel
    #聞き専チャンネル(本番)
    channel = client.get_channel(834104925684105286)
    #聞き専チャンネル(test)
    #channel = client.get_channel(904600089555783720)    

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await tree.sync()
    await client.change_presence(activity=discord.Game(name="🎣釣り"))

@tree.command(
    name="read_def",
    description="読み上げ設定をデフォルトに戻すぞ！"
)
async def read_def(interaction: discord.Interaction):
    with open("./setting.json",'r') as f:
         data=json.load(f)
    
    data['r']="1.2"
    data["fm"]="0"

    with open("./setting.json",'w') as f:
         json.dump(data,f)

    await interaction.response.send_message("読み上げ設定をデフォルトに戻したぜ！！")    
    return

@tree.command(
    name="pitch",
    description="音程を変えるぞ！"
)
@discord.app_commands.describe(
    num="ピッチ(整数)"
)
async def pitch(interaction: discord.Interaction,num:str):
    try:
       mod_pitch(int(num))
       await interaction.response.send_message("ピッチを`"+ str(num) +"`にしたぜ！！")
    except ValueError:
       await interaction.response.send_message("ピッチは整数で入力してくれ！！")
    
    return

@tree.command(
    name="speed",
    description="読み上げのスピードを変えるぞ！"
)
@discord.app_commands.describe(
    speed="読み上げスピード(1.0以上の小数)"
)
async def speed(interaction: discord.Interaction,speed:str):
    #print(speed)
    #print(type(float(speed)))

    try:
       if float(speed) < 1.0:
          await interaction.response.send_message("1.0未満の数はダメだ")
          return
       else:
          mod_speed(float(speed))
          await interaction.response.send_message("読み上げスピードを`"+ str(speed) +"`にしたぜ！！")
    except ValueError:
       await interaction.response.send_message("読み上げスピードは小数で入力してくれ！！")

    return

@tree.command(
    name="join",#コマンド名
    description="ワシがVCに参加するぞ！"#コマンドの説明
)
async def join(interaction: discord.Interaction):
    global channel_ctx
    global channel_id
    #global mem_len
    #print(channel_ctx)
    msg = ["邪魔するぜ!","ワシをお呼びかなぁ?","お前さんを一人にはせえへん","憧れは捨てろ、日々挑戦だ!",""]
    with open("./setting.json",'r') as f:
         data=json.load(f)
    #どこかのVCチャンネルで使われていない場合使えるようにする
    if channel_ctx == 0:
        print('#join')
        print('#voicechannelを取得')
        
        try:
            print(type(interaction.user))
            print(type(interaction.user.voice))
            vc = interaction.user.voice.channel
            print(vc.name)
            print('#voicechannelに接続')
            await vc.connect(timeout=50,reconnect=True)
            await interaction.response.send_message(msg[random.randrange(4)])
            await interaction.followup.send("今のピッチの設定は`"+ str(data['fm']) + "`で,読み上げ速度は`"+str(data['r']+"`だぜ！"))
        except Exception as e:
            print("Error:",e)
           # await interaction.response.send_message("ワシで遊ぶな(｀´）")
            pass

        channel_id = interaction.channel.id
        channel_ctx = 1

    elif channel_ctx == 1:
        await interaction.response.send_message("すまん、使用中だ(;_:)")


@tree.command(
    name="bye",#コマンド名
    description="ワシがVCから出るぞ！"#コマンドの説明
)
async def bye(interaction: discord.Interaction):
    global channel_ctx
    global channel_id
    print('#bye')
    print('#切断')
    await interaction.response.send_message('失礼するぜ!あるじ')
    try:
        await interaction.guild.voice_client.disconnect()
    except:
        pass
    channel_ctx = 0
    channel_id = 0

@tree.command(
    name="log",#コマンド名
    description="ログファイルを出力するぞ！(管理者権限)"#コマンドの説明
)
@discord.app_commands.default_permissions(
    administrator=True
)
async def log(interaction: discord.Interaction):
    await interaction.response.send_message(file=discord.File('./kazumasa.log'),ephemeral=True)

@tree.command(
    name="register",#コマンド名
    description="単語の登録をするぞ！"#コマンドの説明
)
@discord.app_commands.describe(
    word="登録する単語" # 引数名=説明
)
@discord.app_commands.describe(
    read="発音する読み方" # 引数名=説明
)
async def register(interaction: discord.Interaction,word: str,read: str):
    with open('dic.txt', encoding='CP932', mode='a') as f:
        try:
            word1 = mojimoji.han_to_zen(word)
        except:
            pass

        f.write('\n'+ word1 + ',' + read)
        #print('dic.txtに書き込み：''\n'+ arg1 + ',' + arg2)
    await interaction.response.send_message('`' + word +'` を `'+ read +'` として登録したぜ!')


@tree.command(
    name="kazumasa",#コマンド名
    description="ワシの使い方が見れるぞ！"#コマンドの説明
)
async def kazumasa(interaction: discord.Interaction):
    #global channel_id
    #channel_id = ctx.message.channel.id
    embed = discord.Embed(title="読み上げボット(カズマサ)の使い方",description="※読み上げボットとはミュートでボイスチャンネル(VC)にいながらもワシがお前さんの声を代行して読み上げるぞ！下のコマンドはお前さんがVCに入ってる状態でテキストチャンネルに入力するとワシが使えるぞ！",color=discord.Colour.green())
    embed.add_field(name="`/kazumasa`",value="ワシの使い方一覧が表示されるぜ！")
    embed.add_field(name="`/speed` `小数`",value="読み上げスピードがかわるぞ！",inline=False)
    embed.add_field(name="`/pitch` `整数`",value="声の音程がかわるぞ！",inline=False)
    embed.add_field(name="`/read_def`",value="読み上げ推奨設定にするぞ！",inline=False)
    embed.add_field(name="`/join`",value="ワシがVCに参加するぜ！",inline=False)
    embed.add_field(name="`/bye`",value="ワシがVCから抜けるぜ！",inline=False)
    embed.add_field(name="`/register` `単語` `読み方`",value="ワシに発音してほしい単語と読み方をセットしてくれ！",inline=False)
    await interaction.response.send_message(content=None,embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    global channel_ctx
    global channel_id
    global channel
    global mem_id

    #VCに人が入ってきたら
    if after.channel is not None and before.channel is None:
        #VCに聞き専ロールをつけた人が入ってきた場合
        if member.get_role(1266657688570433536) in member.roles:
            if channel_ctx == 0:
                await channel.send(member.name + "さんよ！いらっしゃい！ワシ(読み上げボット)を使うか！？", view=HogeButton())


    #VCからVCへ移動してきた場合
    if after.channel is not None and before.channel is not None:
        #print("channel ctx",str(channel_ctx))
        #前のVCでカズマサが取り残された場合
        if channel_ctx == 1 and mem_id == member.id:
            channel_ctx = 0
            try:
                await member.guild.voice_client.disconnect()
            except Exception as e:
                print(e)

        #聞き専ロールを付与された人が移動した場合
        if member.get_role(1266657688570433536) in member.roles:
            #channel_ctx2 = channel_ctx2 + 1
            if channel_ctx == 0:
                await channel.send(member.name + "さんよ！いらっしゃい！ワシ(読み上げボット)を使うか！？", view=HogeButton())

    #VCから人が抜けて人の人数がゼロの時
    if after.channel is None:
        mem_len_bfr = len(before.channel.members)
        #VCにカズマサのみの時切断する
        if (mem_len_bfr - 1) == 0:
            channel_ctx = 0
            channel_id = 0
            try:
                await member.guild.voice_client.disconnect()
            except Exception as e:
                print(e)
                pass

        #VCに聞き専ロールをつけた人が抜けた場合
        if member.get_role(1266657688570433536) in member.roles:
            if channel_ctx == 1 and member.id == mem_id:
                try:
                    await member.guild.voice_client.disconnect()
                except Exception as e:
                    print(e)
                    pass
                channel_ctx = 0
                mem_id = None
        return 

    return

@client.event
async def on_message(message):
    global channel_id
    if message.author.bot:
        return

    if message.content == "":
        #print("あ")
        return
        
    if message.channel.id == channel_id:
        print('---on_message_start---')
        msgclient = message.guild.voice_client
        print(msgclient)
        if message.channel.id == channel_id and not message.content.startswith("/"):
            if message.guild.voice_client:
                #name = message.author.nick
                #if name == None:
                    #name = message.author.name
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
        #await self.process_commands(message)

        print('---on_message_end---')

#本番用
client.run(TOKEN)
