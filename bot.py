import os
import discord
import json
import json
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import os
from discord.ext.commands import Greedy
import typing
from discord.ext.commands import Context
load_dotenv()
token = os.environ['token']
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix = '$',intents=intents, activity=discord.Game(name='Elden Ring'))
if not os.path.exists('.env'):
    x = input('What is your token?\n')
    with open('.env', 'w') as f:
        f.write('token = ' + x)
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
            print(member.roles, mute)
            if mute not in member.roles:
                await member.add_roles(mute)
                await interaction.response.send_message(f'{member.mention} has been muted for {reason}.')
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
@discord.app_commands.checks.has_permissions(administrator=True)
@app_commands.command(name='unmute', description='unmutes a user.')
async def unmute(interaction: discord.Interaction, member: discord.Member):
    mute = ''
    with open(f'./Files/{interaction.guild.id}.json', 'r') as f:
        x = json.load(f)
        if x['MuteRole'] == False:
            await interaction.response.send_message(f'No mute role set.')
        else:
            mute = discord.utils.get(interaction.guild.roles, id=x['MuteRole']) 
            if mute in member.roles:
                await member.remove_roles(mute)
                await interaction.response.send_message(f'{member.mention} has been unmuted.')
            else:
                await interaction.response.send_message(f'{member.mention} is not muted.')
bot.tree.add_command(unmute)
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

@app_commands.command(name='ping', description='Gets the bots ping')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'Bots ping is {round(bot.latency, 2)}ms', ephemeral=True)
bot.tree.add_command(ping)

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
    #embed.add_field(name=f"/purge <number>", value="purges the last messages from a channel **must have manage message perms**", inline=False)
    #embed.add_field(name=f"/kick <user>", value="kicks a user **must have kick perms**", inline=False)
    #embed.add_field(name=f"/ban <user> <reason>", value="bans a user for the specified reason. **must have ban perms**", inline=False)
    #embed.add_field(name=f"/unban <user>", value="unbans a user. **must have ban perms**", inline=False)
    #embed.add_field(name=f"/search <search terms>", value="allows a user to search youtube and play music", inline=False)
    #embed.add_field(name=f"/stop", value="stops audio play from the bot", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
bot.tree.add_command(help)

bot.run(token)