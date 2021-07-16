# bot.py
from logging import error
import os
import random
import itertools
from aiohttp import payload
import discord
import youtube_dl
import json
from youtube_search import YoutubeSearch
from discord import message
from discord.flags import Intents
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True
intents.reactions = True

prefix = '$'
token = 'Put_Token_here'

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
    print(discord.utils.get(ctx.guild.roles,name="muted"))
    member = ctx.guild.get_member(int(numeric_string))
    await member.add_roles(mute)
    await ctx.send(f'{member.mention} has been muted.')

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
async def search(ctx, *, arg):
    voice_channel = discord.utils.get(ctx.guild.channels, name="music", type="ChannelType.voice")
    results = YoutubeSearch(arg, max_results=5,).to_json()
    json1 = json.loads(results)
    list = ''
    num = 0
    for video in json1['videos']:
        num = num + 1
        list = (list + '\n' + str(num) + ' ' + '`' + video["title"] + '`')
    await ctx.send(list)
    if ctx.channel.message.reference != None:
        print(ctx.channel.last_message.reference)
        num = 0
        for video in json1['videos']:
            num = num + 1
            if num == 1:
                title = video['title']
                video = 'https://www.youtube.com' + video['url_suffix']
        message.edit(f'`{title}` has been selected')
    if ctx.channel.last_message.author :
        num = 0
        for video in json1['videos']:
            num = num + 1
            if num == 2:
                title = video['title']
                video = 'https://www.youtube.com' + video['url_suffix']
        message.edit(f'`{title}` has been selected')    
    if discord.utils.get(message.reactions, emoji='3️⃣', count=2) == True:
        num = 0
        for video in json1['videos']:
            num = num + 1
            if num == 3:
                title = video['title']
                video = 'https://www.youtube.com' + video['url_suffix']
        message.edit(f'`{title}` has been selected')
    if discord.utils.get(message.reactions, emoji='4️⃣', count=2) == True:
        num = 0
        for video in json1['videos']:
            num = num + 1
            if num == 4:
                title = video['title']
                video = 'https://www.youtube.com' + video['url_suffix']
        message.edit(f'`{title}` has been selected')
    if discord.utils.get(message.reactions, emoji='5️⃣', count=2) == True:
        num = 0
        for video in json1['videos']:
            num = num + 1
            if num == 5:
                title = video['title']
                video = 'https://www.youtube.com' + video['url_suffix']
        message.edit(f'`{title}` has been selected')
    


@bot.command()
async def help(ctx):
    await ctx.channel.send(f'how the bot works: \n*{prefix}mute <user>* mutes a user. must have vc mute perms \n*{prefix}unmute <user>* unmutes a user. must have vc mute perms \n*{prefix}purge* <messages to be purged> deleats the most recent messages in a channel. must have manage message perms \n*{prefix}kick <user>* kicks a user. must have kick perms \n*{prefix}ban <user> <reason - not required>* bans a user for the reason specified. must have ban perms. \n*{prefix}unban <user>* unbans a user. must have ban perms.')
    return

bot.run(token)