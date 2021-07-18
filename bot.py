# bot.py
import asyncio
from logging import error
import os
import random
import itertools
import aiohttp
from aiohttp import payload
import discord
import youtube_dl
import json
import urllib
import simplejson
import re
import time
import lxml
from lxml import etree
from discord import message
from discord.flags import Intents
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True
intents.reactions = True

prefix = '$'
token = 'ODY1Mzk3NTM3NzYxMTMyNTQ1.YPDaQw.QZio2XKwmh6PvDjYm70Q_5f1JyM'

bot = commands.Bot(command_prefix = prefix, intents=intents, activity=discord.Game(name=f'{prefix}help'), help_command=None)

@bot.event
async def on_guild_join(guild):
    muted = discord.utils.get(guild.roles, name="muted")
    if muted == None:
        await guild.create_role(name="muted")
        muted = discord.utils.get(guild.roles, name="muted")
    for channel in guild.channels:
        await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    return

@bot.command()
@commands.has_permissions(administrator = True)
async def mute(ctx, arg):
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    member = ctx.guild.get_member(int(numeric_string))
    await member.add_roles(mute)
    await ctx.channel.send(f'{member.mention} has been muted.')

@bot.command()
@commands.has_permissions(administrator = True)
async def unmute(ctx, arg):
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    member = ctx.guild.get_member(int(numeric_string))
    await member.remove_roles(mute)
    await ctx.send(f'{member.mention} has been unmuted.')

@bot.command()
@commands.has_permissions(administrator = True)
async def purge(ctx, arg: int):
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=arg + 1):
        messages.append(message)
    await channel.delete_messages(messages)
    await channel.send(f"Successfully removed the last {arg} messages")

@bot.command()
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked')

@bot.command()
@commands.has_permissions(administrator = True)
async def ban(ctx, member: discord.Member, *, reason=None):
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
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f'Unbanned {user.mention}')
            return



@bot.command()
async def search(ctx,*, arg):
    search_keyword=str(arg)
    keyword = search_keyword.replace(' ', '+')
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    num = 0
    list = ''
    message = await ctx.send('searching...')
    message
    while num < 5:
        video = "https://www.youtube.com/watch?v=" + video_ids[num]
        ydl_opts = {}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
        list = list + str(num + 1) + ' ' + '`' + video_title + '`' + '\n'
        num += 1
    await message.edit(content=list)
    await message.add_reaction('1\N{variation selector-16}\N{combining enclosing keycap}')
    await message.add_reaction('2\N{variation selector-16}\N{combining enclosing keycap}')
    await message.add_reaction('3\N{variation selector-16}\N{combining enclosing keycap}')
    await message.add_reaction('4\N{variation selector-16}\N{combining enclosing keycap}')
    await message.add_reaction('5\N{variation selector-16}\N{combining enclosing keycap}')
    def check(reaction, user):
        return user == ctx.author
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
    except asyncio.TimeoutError:
        await ctx.channel.send(f'{ctx.author.mention}, Your request has timed out.')
    else:
        print(reaction)
        if str(reaction) == '1\N{variation selector-16}\N{combining enclosing keycap}':
            num = 0
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(content='Selected: \n `' + video_title + '`')
            member = ctx.guild.get_member(int(ctx.author.id))
            if member.voice.channel.id != None:
                print(member.voice.channel.id)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './video0.mp3'
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print(video_id)
                    ydl.download(['https://www.youtube.com/watch?v=' + str(video_id)])
                member.voice.channel.connect
                channel = member.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(source="./video0.mp3"))
                while vc.is_playing():
                    time.sleep(.1)
                os.remove('./video0.mp3')
            else:
                ctx.send(f"silly {member.mention}, you must be in a voice channel to do this!")
        if str(reaction) == '2\N{variation selector-16}\N{combining enclosing keycap}':
            num = 1
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(content='Selected: \n `' + video_title + '`')
            member = ctx.guild.get_member(int(ctx.author.id))
            if member.voice.channel.id != None:
                print(member.voice.channel.id)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './video0.mp3'
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print(video_id)
                    ydl.download(['https://www.youtube.com/watch?v=' + str(video_id)])
                member.voice.channel.connect
                channel = member.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(source="./video0.mp3"))
                while vc.is_playing():
                    time.sleep(.1)
                os.remove('./video0.mp3')
            else:
                ctx.send(f"silly {member.mention}, you must be in a voice channel to do this!")
        if str(reaction) == '3\N{variation selector-16}\N{combining enclosing keycap}':
            num = 2
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(content='Selected: \n `' + video_title + '`')
            member = ctx.guild.get_member(int(ctx.author.id))
            if member.voice.channel.id != None:
                print(member.voice.channel.id)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './video0.mp3'
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print(video_id)
                    ydl.download(['https://www.youtube.com/watch?v=' + str(video_id)])
                member.voice.channel.connect
                channel = member.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(source="./video0.mp3"))
                while vc.is_playing():
                    time.sleep(.1)
                os.remove('./video0.mp3')
            else:
                ctx.send(f"silly {member.mention}, you must be in a voice channel to do this!")
        if str(reaction) == '4\N{variation selector-16}\N{combining enclosing keycap}':
            num = 3
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(content='Selected: \n `' + video_title + '`')
            member = ctx.guild.get_member(int(ctx.author.id))
            if member.voice.channel.id != None:
                print(member.voice.channel.id)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './video0.mp3'
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print(video_id)
                    ydl.download(['https://www.youtube.com/watch?v=' + str(video_id)])
                member.voice.channel.connect
                channel = member.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(source="./video0.mp3"))
                while vc.is_playing():
                    time.sleep(.1)
                os.remove('./video0.mp3')
            else:
                ctx.send(f"silly {member.mention}, you must be in a voice channel to do this!")
        if str(reaction) == '5\N{variation selector-16}\N{combining enclosing keycap}':
            num = 4
            video = "https://www.youtube.com/watch?v=" + video_ids[num]
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video, download=False)
                video_url = info_dict.get("url", None)
                video_id = info_dict.get("id", None)
                video_title = info_dict.get('title', None)
            await message.edit(content='Selected: \n `' + video_title + '`')
            member = ctx.guild.get_member(int(ctx.author.id))
            if member.voice.channel.id != None:
                print(member.voice.channel.id)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': './video0.mp3'
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    print(video_id)
                    ydl.download(['https://www.youtube.com/watch?v=' + str(video_id)])
                member.voice.channel.connect
                channel = member.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(source="./video0.mp3"))
                while vc.is_playing():
                    time.sleep(.1)
                os.remove('./video0.mp3')
            else:
                ctx.send(f"silly {member.mention}, you must be in a voice channel to do this!")

@bot.command
async def stop(ctx):
    print('this is a placholder for a future command to stop audio')


@bot.command()
async def ping(ctx):
    ping_ = bot.latency
    ping =  round(ping_ * 1000)
    await ctx.send(f"my ping is {ping}ms")

    


@bot.command()
async def help(ctx):
    await ctx.channel.send(f'how the bot works: \n*{prefix}mute <user>* mutes a user. must have vc mute perms \n*{prefix}unmute <user>* unmutes a user. must have vc mute perms \n*{prefix}purge* <messages to be purged> deleats the most recent messages in a channel. must have manage message perms \n*{prefix}kick <user>* kicks a user. must have kick perms \n*{prefix}ban <user> <reason - not required>* bans a user for the reason specified. must have ban perms. \n*{prefix}unban <user>* unbans a user. must have ban perms.')
    return

bot.run(token)