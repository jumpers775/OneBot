# bot.py
from asyncio.windows_events import NULL
from logging import error
import os
import random
import itertools


import discord
from discord import message
from discord.flags import Intents
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents, activity=discord.Game(name='!help'))

token = 'Set_Token_here'


@client.event
async def on_guild_join(guild):
    await guild.create_text_channel('codes')
    await guild.create_text_channel('verify')
    await guild.create_text_channel('sent-codes')
    await guild.create_role(name="Access")
    await guild.create_role(name="muted")
    await guild.create_role(name="Non-Access")
    return

@client.event
async def on_member_join(member):
    defaultrole = discord.utils.get(message.guild.roles, name='Non-Access') 
    role = message.guild.get_role(defaultrole.id)
    await member.add_roles(role)
    return

@client.event
async def on_message(message):
    genchannel = discord.utils.get(message.guild.channels, name='codes')
    authchannel = discord.utils.get(message.guild.channels, name='verify')
    logchannel = discord.utils.get(message.guild.channels, name='sent-codes')
    allowedrole = discord.utils.get(message.guild.roles, name='Access')
    muterole = discord.utils.get(message.guild.roles, name='muted')
    defaultrole = discord.utils.get(message.guild.roles, name='Non-Access') 
    if message.content.startswith('!gen'):
        if message.channel == client.get_channel(genchannel.id):
            random_id = ''.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
            numeric_filter = filter(str.isdigit, message.content)
            numeric_string = "".join(numeric_filter)   
            user = await client.fetch_user(int(numeric_string))
            await user.send(f"you've been invited to Join {message.guild}! Go to the verification channel and type ``!verify " + random_id + '``')
            channel = client.get_channel(int(logchannel.id))
            vnum = numeric_string + random_id
            await channel.send(vnum)
            channel3_id = int(message.channel.id)
            channel = client.get_channel(channel3_id)
            await channel.send('Code for @' + str(user) + ' sucessfully generated')
    if message.content.startswith('!verify'):
            if message.channel == client.get_channel(authchannel.id):
                author = message.author
                channel1 = message.channel
                numeric_filter = filter(str.isdigit, message.content)
                numeric_string = "".join(numeric_filter) 
                num = str(message.author.id) + str(numeric_string)
                channel = client.get_channel(logchannel.id)
                messages = await channel.history(limit=200).flatten()
                for message in messages:
                    if num in message.content:
                        mid = message.id
                        if mid > 0:
                            channel = channel1
                            await channel.send('Congratulations! you are now verified to enter the server.')
                            role = message.guild.get_role(allowedrole.id)
                            oldrole = message.guild.get_role(defaultrole.id)
                            await author.add_roles(role)
                            await author.remove_roles(oldrole)
                            await client.http.delete_message(logchannel.id, mid)
                        break
    if message.content.startswith('!mute') :
        if message.author.guild_permissions.administrator == True:
            numeric_filter = filter(str.isdigit, message.content)
            numeric_string = "".join(numeric_filter) 
            member = message.guild.get_member(int(numeric_string))
            if member != None:
                muted = message.guild.get_role(muterole.id)
                await member.add_roles(muted)
                await message.channel.send(f'{member.mention} has been muted')
                return
            else:
                await message.channel.send('User does not exist. Please try again.')
                return
        else:
            await message.channel.send('Invalid permissions. You must be a server admin to run this command')
    if message.content.startswith('!unmute'):
        if message.author.guild_permissions.administrator == True:
            numeric_filter = filter(str.isdigit, message.content)
            numeric_string = "".join(numeric_filter) 
            member = message.guild.get_member(int(numeric_string))
            if member != None:
                muted = message.guild.get_role(muterole.id)
                await member.remove_roles(muted)
                await message.channel.send(f'{member.mention} has been unmuted')
                return
            else:
                await message.channel.send('User does not exist. Please try again.')
                return
        else:
            await message.channel.send('Invalid permissions. You must be a server admin to run this command')
            return
    if message.content.startswith('!help'):
        await message.channel.send('use !gen *user id* -- Generates an invitation code for a user. **MUST BE ADMIN TO USE**')
        await message.channel.send('use !verify *generated code* -- adds the user to the whitelist. **must be run in a set verification channel**')
        await message.channel.send('use !mute *user id* -- mutes a user. **MUST BE ADMIN TO USE**')
        await message.channel.send('use !unmute *user id* -- unmutes a user. **MUST BE ADMIN TO USE**')
        await message.channel.send('use !purge *number of messages to be purged* -- deletes messages from a channel')
        await message.channel.send('use !help -- displays this page.')
        return
    if message.content.startswith('!purge'):
        if message.author.guild_permissions.administrator == True:
            numeric_filter = filter(str.isdigit, message.content)
            numeric_string = "".join(numeric_filter) 
            channel = message.channel
            messages = []
            async for message in channel.history(limit=int(numeric_string) + 1):
              messages.append(message)
            await channel.delete_messages(messages)

client.run(token)