# bot.py
import asyncio
from logging import error
import os
from dotenv import dotenv_values
import random
import itertools
import aiohttp
from aiohttp import payload
import discord
import youtube_dl
import json
import urllib
import re
import json
import time
import ffmpeg
from youtubesearchpython.__future__ import VideosSearch
from discord import message
from dotenv import load_dotenv
from discord.flags import Intents
from discord.ext import commands
import os.path
from os import path
import sys
import subprocess
import pkg_resources
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
prefix = '$'
bot = commands.Bot(command_prefix = prefix, intents=intents, activity=discord.Game(name=f'{prefix}help'), help_command=None)
bot.queue = {}
def startcheck():
    if path.exists("./.env") == False:
        env = open('./.env', 'w')
        t = input("Please input your bot token:")
        print(f"The Token {t} has been set. to change this edit the .env file in this directory")
        env.write(f"token={t}")
    if path.exists("./xp.json ") == False:
        exp = {}
        with open("xp.json", "w") as write_file:
            json.dump(exp, write_file, indent=4)  
startcheck()
load_dotenv()
token = os.environ['token']
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        ytdl = youtube_dl.YoutubeDL(ydl_opts)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        ffmpeg_options = {
            'options': '-vn'
        }
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
@bot.event
async def on_guild_join(guild):
    print(f"guild {guild} has been joined.")
    await guild.create_text_channel('logs')
    whitelisted = discord.utils.get(guild.roles, name="whitelisted")
    everyone = discord.utils.get(guild.roles, name="everyone")
    p = 0
    for channel in guild.channels:
        if p < 0:
            p += 1
            f = channel.send('would you like to enable whitelisting?')
            f
            reacts = '\N{THUMBS UP SIGN}'
            await message.add_reaction(reacts)
            reacts = '\N{THUMBS DOWN SIGN}'
            await message.add_reaction(reacts)
            def check(reaction, user):
                x = False
                if user.server_permissions.administrator:
                    x = True
                return x
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
            except asyncio.TimeoutError:
                await f.reply('Timed out, disabling')
            else:
                if str(reaction) != '\N{THUMBS UP SIGN}':
                    if whitelisted == None:
                        await guild.create_role(name="whitelisted")
                    for channel in guild.channels:
                        if channel.name != 'rules' or channel.name != 'Rules' or channel.name != 'Welcome' or channel.name != 'welcome':
                            await channel.set_permissions(everyone, speak=False, send_messages=False, read_message_history=True, read_messages=False)
                if str(reaction) != '\N{THUMBS DOWN SIGN}':
                    return
    muted = discord.utils.get(guild.roles, name="muted")
    if muted == None:
        await guild.create_role(name="muted")
        muted = discord.utils.get(guild.roles, name="muted")
    for channel in guild.channels:
        await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    musician = discord.utils.get(guild.roles, name="musician")
    if musician == None:
        await guild.create_role(name="musician")
    DJ = discord.utils.get(guild.roles, name="DJ")
    if DJ == None:
        await guild.create_role(name="DJ")
    with open('xp.json', 'r+') as f:
        data = json.load(f)
        if guild.id not in data:
            data[guild.id] = {}
        for member in guild.members:
            if member.id != bot.user.id:
                guilddata = data[guild.id]
                if str(member.id) not in guilddata:
                    data[guild.id][member.id] = 0
        f.seek(0)
        json.dump(data, f, indent=4)
    print(f'initial setup complete for {guild}')
    return
@bot.command()
@commands.has_permissions(administrator = True)
async def mute(ctx, arg):
    print(f'command mute used by {ctx.author}')
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    member = ctx.guild.get_member(int(numeric_string))
    await member.add_roles(mute)
    await ctx.channel.send(f'{member.mention} has been muted.')
@bot.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx, arg):
    print(f'command unmute used by {ctx.author}')
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    member = ctx.guild.get_member(int(numeric_string))
    await member.remove_roles(mute)
    await ctx.send(f'{member.mention} has been unmuted.')

@bot.command()
@commands.has_permissions(administrator = True)
async def purge(ctx, arg: int):
    print(f'command purge used by {ctx.author}. the last {arg} messages will be attempted to be deleated.')
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=arg + 1):
        messages.append(message)
    await channel.delete_messages(messages)
    await channel.send(f"Successfully removed the last {arg} messages")

@bot.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason=None):
    print(f'command kick used by {ctx.author}')
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked')

@bot.command()
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason=None):
    print(f'command ban used by {ctx.author}')
    if member == None:
        await ctx.channel.send("Could not find user.")
        return
    if member == ctx.message.author:
        await ctx.channel.send('You cant ban yourself!')
        return
    if reason == None:
        reason = "Repeated rule violations"
    message = f"You have been banned from {ctx.guild.name} for {reason}"
    await member.send(message)
    await member.ban(reason=reason)
    await ctx.channel.send(f"{member} is banned for {reason}")

@bot.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    print(f'command unban used by {ctx.author}')
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f'Unbanned {user.mention}')
            return

@bot.command()
async def stop(ctx):
    print(f'user {ctx.author} has used the stop command')
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    musician = discord.utils.get(ctx.guild.roles,name="musician")
    DJ = discord.utils.get(ctx.guild.roles,name="DJ")
    if voice != None:
        if musician in ctx.author.roles or ctx.author.guild_permissions.administrator == True or DJ in ctx.author.roles: 
            if musician in ctx.author.roles:
                await ctx.author.remove_roles(musician)
            await voice.disconnect(force=True)
            await ctx.reply('stopped')
        else:
            await ctx.reply(f'you do not have the proper permissions to use this')
    else:
        await ctx.reply('Im not in a voice channel.')

@bot.command()
async def search(ctx, *, arg):
    print(f'command search used by {ctx.author}')
    message = await ctx.reply('searching...')
    message
    ydl_opts = {'format': 'bestaudio', 'noplaylist':'True'}
    videosSearch = VideosSearch(arg, limit = 5)
    videosResult = await videosSearch.next()
    id1 = videosResult['result'][0]['link'].replace('https://www.youtube.com/watch?v=', '')
    id2 = videosResult['result'][1]['link'].replace('https://www.youtube.com/watch?v=', '')
    id3 = videosResult['result'][2]['link'].replace('https://www.youtube.com/watch?v=', '')
    id4 = videosResult['result'][3]['link'].replace('https://www.youtube.com/watch?v=', '')
    id5 = videosResult['result'][4]['link'].replace('https://www.youtube.com/watch?v=', '')
    video_ids = [id1,id2,id3,id4,id5]
    num = 0
    list = ''
    embed=discord.Embed(
        title="Results",
        description="Heres what I found:",
        color=discord.Color.dark_gold())
    while num < 5:
        video = "https://www.youtube.com/watch?v=" + video_ids[num]
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
        list = list + str(num + 1) + ' ' + '`' + video_title + '`' + '\n'
        embed.add_field(name=f'Result {num + 1}:', value=f"{video_title}", inline=False)
        num += 1
    await message.edit(embed=embed, content='')
    rnum = 1
    while rnum < 6:
        reacts = str(rnum) + '\N{variation selector-16}\N{combining enclosing keycap}'
        await message.add_reaction(reacts)
        rnum += 1
    await message.add_reaction('\U0001f6d1')
    def check(reaction, user):
        return user == ctx.author
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
        await ctx.channel.reply(f'{ctx.author.mention}, Your request has timed out.')
    else:
        if str(reaction) != '\U0001f6d1':
            rep = str(reaction)
            num = int(rep.replace('\N{variation selector-16}\N{combining enclosing keycap}', '')) - 1
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(embed=embed, content='')
            member = ctx.guild.get_member(int(ctx.author.id))
            if ctx.author.voice.channel.id != None:
                embed=discord.Embed(
                    title="Selected:",
                    description=f"{video_title}",
                    color=discord.Color.dark_gold())
                embed.add_field(name=f'status', value=f"queued", inline=False)
                await message.edit(embed=embed)
                if ctx.guild.id not in bot.queue:
                    vid = []
                    bot.queue[ctx.guild.id] = vid
                video_url = f'https://www.youtube.com/watch?v={video_id}'  
                lists = bot.queue[ctx.guild.id]
                lists.append(video_url)
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                channel = ctx.author.voice.channel
                musician = discord.utils.get(ctx.guild.roles,name="musician")
                await ctx.author.add_roles(musician)
                if video_url == lists[0]:
                    vc = await channel.connect()
                    while 0 <= 0 < len(lists) == True:
                        videolink = lists[0]
                        audio = await YTDLSource.from_url(videolink, loop=bot.loop, stream=True)
                        vc.play(audio)
                        while vc.is_playing():
                            await asyncio.sleep(.1)
                        lists.pop(0)
                    vc.stop()
                    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                    if voice != None:
                        await vc.disconnect(force=True)
                    await ctx.author.remove_roles(musician)
                    audio.cleanup()                
            else:
                await ctx.reply('could not complete this request as im already in a voice channel')
                embed=discord.Embed(
                    title="Selected:",
                    description=f"{video_title}",
                    color=discord.Color.dark_gold())
                embed.add_field(name=f'status', value=f"playback ended", inline=False)
                await message.edit(embed=embed)
        if str(reaction) == '\U0001f6d1':
            await ctx.reply('This request has been canceled.')

async def download(url, name):
  async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
         data = await response.content.read()
         with open(name, "wb") as f:
               f.write(data)
@bot.listen('on_message')
async def on_message(message):
    if message.author.id != bot.user.id:
        channel = discord.utils.get(message.guild.text_channels, name="logs")
        if message.attachments == []:
            await channel.send(f'`{message.channel}` : `{message.author}` : {message.content}')
        else:
            url = str(message.attachments[0])
            names = 1
            name = url[url.rindex('.')+1:]
            file = ''
            while path.exists(f'./{names}.{name}') == True:
                names += 1
            file = f'{str(names)}.{name}'
            await download(url, file)
            await channel.send(f'`{message.channel}` : `{message.author}` : {message.content}', file=discord.File(f'./{file}'))
            os.remove(f'./{file}')
@bot.listen('on_message')
async def on_message(message):
    if message.author.id != bot.user.id:
        with open('xp.json', 'r+') as f:
            data = json.load(f) 
            data[str(message.author.guild.id)][str(message.author.id)] += 1
            remainder = data[str(message.author.guild.id)][str(message.author.id)] % 20
            is_divisible = remainder == 0
            if is_divisible == True:
                rolename = f"level {remainder + 1}"
                await message.channel.send(f'Congrats {message.author.mention} on level {remainder + 1}!')
                role = discord.utils.get(message.guild.roles, name=str(rolename))
                if role == None:
                    await message.guild.create_role(name=str(rolename))
                    role = discord.utils.get(message.guild.roles, name=str(rolename))
                member = message.guild.get_member(message.author.id)
                await member.add_roles(role)
            else:
                num = 9
                numb = data[str(message.author.guild.id)][str(message.author.id)] 
                while num > 0:
                    remainder = numb % 20
                    is_divisible = remainder == 0
                    role = discord.utils.get(message.guild.roles, name=f"level {remainder + 1}")
                    if is_divisible == True and role not in message.author.roles:
                        rolename = f"level {remainder + 1}"
                        await message.channel.send(f'Congrats {message.author.mention} on level {remainder + 1}!')
                        role = discord.utils.get(message.guild.roles, name=str(rolename))
                        if role == None:
                            await message.guild.create_role(name=str(rolename))
                            role = discord.utils.get(message.guild.roles, name=str(rolename))
                        member = message.guild.get_member(message.author.id)
                        await member.add_roles(role)

            f.seek(0)
            json.dump(data, f, indent=4)
@bot.listen('on_member_join')
async def on_member_join(member):
    print(f"{member} has joined {member.guild}")
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    await channel.send(f"Welcome, {member.mention} to {member.guild}!")
    with open('xp.json', 'r+') as f:
        data = json.load(f)
        guilddata = data[str(member.guild.id)]
        if str(member.id) not in guilddata:
            data[str(member.guild.id)][str(member.id)] = 0
        f.seek(0)
        json.dump(data, f, indent=4)
@bot.event
async def on_ready():
    print(f'{bot.user.name} has started up')
@bot.command()
async def ping(ctx):
    ping_ = bot.latency
    ping =  round(ping_ * 1000)
    await ctx.reply(f"my ping is {ping}ms")
@bot.command()
async def setxp(ctx, arg,arg2):
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    member = ctx.guild.get_member(int(numeric_string))
    with open('xp.json', 'r+') as f:
        data = json.load(f)
        data[str(ctx.guild.id)][str(member.id)] = int(arg2)
        f.seek(0)
        json.dump(data, f, indent=4)
    await ctx.reply(f"{member.mention}'s XP has been set to {arg2}")
@bot.command()
async def stats(ctx, arg=None):
    if arg == None:
        arg = ctx.author.id
    else:
        numeric_filter = filter(str.isdigit, arg)
        arg = "".join(numeric_filter)
    member = ctx.guild.get_member(arg)
    with open('xp.json', 'r+') as f:
        data = json.load(f)
        num = data[str(ctx.guild.id)][str(arg)]
        embed=discord.Embed(
        title="Stats:",
            description=f"{member}'s stats:",
            color=discord.Color.blurple())
        embed.add_field(name=f'XP:', value=f"*{num}*", inline=False)
        await ctx.reply(embed=embed)       
@bot.command()
async def help(ctx):
    print(f'user {ctx.author} used command help')
    embed=discord.Embed(
    title="Commands",
        description="How the bot works:",
        color=discord.Color.blurple())
    embed.add_field(name=f'{prefix}mute <user>', value="mutes a user. **must have mute perms**", inline=False)
    embed.add_field(name=f"{prefix}unmute <user>", value="unmutes a user. **must have mute perms**", inline=False)
    embed.add_field(name=f"{prefix}purge <number>", value="purges the last messages from a channel **must have manage message perms**", inline=False)
    embed.add_field(name=f"{prefix}kick <user>", value="kicks a user **must have kick perms**", inline=False)
    embed.add_field(name=f"{prefix}ban <user> <reason>", value="bans a user for the specified reason. **must have ban perms**", inline=False)
    embed.add_field(name=f"{prefix}unban <user>", value="unbans a user. **must have ban perms**", inline=False)
    embed.add_field(name=f"{prefix}search <search terms>", value="allows a user to search youtube and play music", inline=False)
    embed.add_field(name=f"{prefix}stop", value="stops audio play from the bot", inline=False)
    await ctx.reply(embed=embed)
    return
bot.run(token)
