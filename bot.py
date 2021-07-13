# bot.py
from asyncio.windows_events import NULL
from logging import error
import os
import random
import itertools
import discord
from discord import message
from discord.flags import Intents
from discord.ext import commands
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = '!', intents=intents, activity=discord.Game(name='!help'))
token = 'PUT_TOKEN_HERE'

@bot.event
async def on_guild_join(guild):
    await guild.create_role(name="muted")
    muted = discord.utils.get(guild.roles, name="muted")
    for channel in guild.channels:
        await channel.set_permissions(muted, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    return

@bot.command()
@commands.has_permissions(mute_members = True)
async def mute(ctx, arg):
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    print(discord.utils.get(ctx.guild.roles,name="muted"))
    member = ctx.guild.get_member(int(numeric_string))
    await member.add_roles(mute)
    await ctx.send(f'{member.mention} has been muted.')

@bot.command()
@commands.has_permissions(mute_members = True)
async def unmute(ctx, arg):
    numeric_filter = filter(str.isdigit, arg)
    numeric_string = "".join(numeric_filter)
    mute = discord.utils.get(ctx.guild.roles,name="muted")
    member = ctx.guild.get_member(int(numeric_string))
    await member.remove_roles(mute)
    await ctx.send(f'{member.mention} has been unmuted.')

@bot.command()
@commands.has_permissions(manage_messages = True)
async def purge(ctx, arg: int):
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=arg + 1):
        messages.append(message)
    await channel.delete_messages(messages)
    await channel.send(f"Successfully removed the last {arg} messages")

@bot.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked')

@bot.command()
@commands.has_permissions(ban_members = True)
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
@commands.has_permissions(ban_members = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.channel.send(f'Unbanned {user.mention}')
            return

bot.run(token)
