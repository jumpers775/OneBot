Version = '3.0.0b2'
import os
import discord
import aiohttp
import json
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import os
import datetime
from discord.ext.commands import Greedy
import typing
from discord.ext.commands import Context
async def checkurl(url: str):
    try:
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as resp:
               return resp.status == 200
    except:
        return False
if not os.path.exists('.env'):
    x = input('What is your token?\n')
    with open('.env', 'w') as f:
        f.write('token = ' + x)
load_dotenv()
token = os.environ['token']
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix = '$',intents=intents, activity=discord.Game(name='Elden Ring'))
if not os.path.isdir('./Files'):
    os.mkdir('./Files')
@bot.event
async def on_ready():
    for a in bot.guilds:
        if not os.path.exists(f'./Files/{a.id}.json'):
            with open(f'./Files/{a.id}.json', 'w') as f:
                x = {"MuteRole":False}
                json.dump(x, f)
    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    bot.starttime = datetime.datetime.now()
    print(f'{bot.user} has connected to Discord!')


@bot.command()
@commands.is_owner()
async def sync(ctx: Context, guilds: Greedy[discord.Object], spec: typing.Optional[typing.Literal["~"]] = None) -> None:
    if not guilds:
        if spec == "~":
            bot.tree.copy_global_to(guild=ctx.guild)
            fmt = await bot.tree.sync(guild=ctx.guild)
        else:
            fmt = await bot.tree.sync()
        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    assert guilds is not None
    fmt = 0
    for guild in guilds:
        try:
            await bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            fmt += 1

    await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")@commands.is_owner()


@discord.app_commands.checks.has_permissions(administrator=True)
@app_commands.command(name='mute', description='Mutes a user.')
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str):
    mute = ''
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        if x['MuteRole'] == False:
            await interaction.response.send_message(f'No mute role set.')
        else:
            mute = discord.utils.get(interaction.guild.roles, id=x['MuteRole']) 
            if mute not in member.roles:
                try:
                    await member.add_roles(mute)
                    await interaction.response.send_message(f'{member.mention} has been muted for {reason}.')
                except discord.Forbidden:
                    await interaction.response.send_message(f'I do not have permission to mute {member.mention}.')
            else:
                await interaction.response.send_message(f'{member.mention} has already been muted.')

@mute.autocomplete('reason')
async def mute_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> typing.List[app_commands.Choice[str]]:
    mutes = ['repeated rule violations', 'spamming', 'advertising', 'harassment', 'threatening', 'insulting', 'flooding', 'other']
    return [
        app_commands.Choice(name=mute, value=mute)
        for mute in mutes if current.lower() in mute.lower()
    ]
bot.tree.add_command(mute)
@mute.error
async def mute_error(interaction: discord.Interaction, error: Exception):
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        mute = discord.utils.get(interaction.guild.roles, id=x['MuteRole'])
        if mute == None:
            await interaction.response.send_message(f'Mute role invalid.', ephemeral=True)
        else:
            await interaction.response.send_message('admin privileges are required to use this command.', ephemeral=True)


@discord.app_commands.checks.has_permissions(administrator=True)
@app_commands.command(name='unmute', description='unmutes a user.')
async def unmute(interaction: discord.Interaction, member: discord.Member):
    mute = ''
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        if x['MuteRole'] == False:
            await interaction.response.send_message(f'No mute role set.')
        else:
            try:
                mute = discord.utils.get(interaction.guild.roles, id=x['MuteRole'])
            except:
                await interaction.response.send_message('Mute role invalid.') 
            if mute in member.roles:
                try:
                    await member.remove_roles(mute)
                    await interaction.response.send_message(f'{member.mention} has been unmuted.')
                except discord.Forbidden:
                    await interaction.response.send_message(f'I do not have permission to unmute {member.mention}.')
            else:
                await interaction.response.send_message(f'{member.mention} is not muted.')
bot.tree.add_command(unmute)
@unmute.error
async def unmute_error(interaction: discord.Interaction, error: Exception):
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        mute = discord.utils.get(interaction.guild.roles, id=x['MuteRole'])
        if mute == None:
            await interaction.response.send_message(f'Mute role invalid.', ephemeral=True)
        else:
            await interaction.response.send_message('admin privileges are required to use this command.', ephemeral=True)

@discord.app_commands.checks.has_permissions(administrator=True)
@app_commands.command(name='createmuterole', description='creates the mute role.')
async def createmuterole(interaction: discord.Interaction, role: str):
    await interaction.guild.create_role(name=role)
    role = discord.utils.get(interaction.guild.roles, name=role)
    for channel in interaction.guild.channels:
        await channel.set_permissions(
            role,
            send_messages=False,
            add_reactions=False,
            speak=False,
        )
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        x['MuteRole'] = role.id
        with open(f'./Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(x, f)
    await interaction.response.send_message(f'Mute role created and set to {role.mention}.')

@createmuterole.error
async def setmuterole_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message('admin privilages are required to use this command.', ephemeral=True)
bot.tree.add_command(createmuterole)


@app_commands.command(name='uptime', description='check how long the bot has been online.')
async def uptime(interaction: discord.Interaction):
    time = datetime.datetime.now() - bot.starttime
    p = str(time).split('.')[0].split(':')
    k = int(p[0]) if ',' not in str(p[0]) else int(p[0].split(',')[1])
    m = False if ',' not in str(p[0]) else str(p[0].split(',')[0]).split(' ')[0]
    x = f'''{f"{str(int(p[2]))} {'Seconds' if int(p[2]) > 1 else 'Second'}" if int(p[2]) > 0 else ''}'''
    y = f'''{f"{str(int(p[1]))} {'Minutes' if int(p[1]) > 1 else 'Minute'}{', ' if int(p[2]) > 0 else ''}" if int(p[1]) > 0 else ""}'''
    z = f'''{f"{str(int(k))} {'Hours' if int(k) > 1 else 'Hour'}{', ' if int(p[1]) > 0 or int(p[2]) > 0 else ''}" if int(k) != 0 else ""}'''
    l = f'''{f'{m} {"Days" if int(m) > 1 else "Day"}{", " if int(k) > 0 or int(p[1]) > 0 or int(p[2]) > 0 else ""}' if m != False else ''}'''
    await interaction.response.send_message('Uptime:\n' + l + z + y + x, ephemeral=True)
bot.tree.add_command(uptime)


@discord.app_commands.checks.has_permissions(administrator=True)
@app_commands.command(name='setmuterole', description='Sets the mute role.')
async def setmuterole(interaction: discord.Interaction, role: discord.Role):
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        x['MuteRole'] = role.id
        with open(f'./Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(x, f)
    await interaction.response.send_message(f'Mute Role has been set to {role.name}')
bot.tree.add_command(setmuterole)
@setmuterole.error
async def setmuterole_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message('admin privilages are required to use this command.', ephemeral=True)

@app_commands.command(name='ping', description='Gets the bots ping')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Bots ping is {round(bot.latency, 2)}ms', ephemeral=True)
bot.tree.add_command(ping)

@app_commands.command(name='version', description='Bot version info.')
async def ver(interaction: discord.Interaction):
    await interaction.response.send_message(f'I am {bot.user.name} version {Version}.\nMy source code can be found at {f"https://github.com/jumpers775/OneBot/releases/tag/{Version}" if  await checkurl(f"https://github.com/jumpers775/OneBot/releases/tag/{Version}") else "https://github.com/jumpers775/OneBot"}', ephemeral=True, suppress_embeds=True)
bot.tree.add_command(ver)

@app_commands.command(name='help', description='Help command.')
async def help(interaction: discord.Interaction):
    embed=discord.Embed(
    title="Commands",
        description="How the bot works:",
        color=discord.Color.blurple())
    embed.add_field(name=f'/ping', value="gets bots ping.", inline=False)
    embed.add_field(name=f'/mute <user> <reason>', value="mutes a user. **must have admin perms**", inline=False)
    embed.add_field(name=f"/unmute <user>", value="unmutes a user. **must have admin perms**", inline=False)
    embed.add_field(name=f"/help ", value="displays this page", inline=False)
    embed.add_field(name=f"/uptime ", value="shows bots uptime", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
bot.tree.add_command(help)

@app_commands.command(name='invite', description='Invite link.')
async def invite(interaction: discord.Interaction):
    await interaction.response.send_message(f'Invite link: https://discord.com/oauth2/authorize?client_id={bot.application_id}&permissions=8&scope=bot%20applications.commands', ephemeral=True)
bot.tree.add_command(invite)


bot.run(token)
