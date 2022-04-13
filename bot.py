Version = '3.0.0b3'
import os
import ffmpeg
import discord
import aiohttp
import asyncio
import json
from requests import options
import youtube_dl
from youtube_search import YoutubeSearch
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
async def on_member_join(member):
    with open(f'./Files/{member.guild.id}.json', 'r') as f:
        data = json.load(f)
        if member.id not in data['xp']:
            data['xp'][member.id] = 0
            with open(f'./Files/{member.guild.id}.json', 'w') as f:
                json.dump(data, f)

@bot.event
async def on_ready():
    for a in bot.guilds:
        if not os.path.exists(f'./Files/{a.id}.json'):
            with open(f'./Files/{a.id}.json', 'w') as f:
                x = {"MuteRole":False,"xp":False}
                json.dump(x, f)
    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        with open(f'./Files/{guild.id}.json', 'r') as f:
            x = json.load(f)
            if len(guild.members) != len(x['xp']):
                for member in guild.members:
                    if member.id not in x['xp']:
                        x['xp'][member.id] = 0
                with open(f'./Files/{guild.id}.json', 'w') as f:
                    json.dump(x, f)
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
    embed.add_field(name=f"/stats <user>", value="shows users stats", inline=False)
    embed.add_field(name=f"/version ", value="shows bots version", inline=False)
    embed.add_field(name=f"/setmuterole <role>", value="sets the mute role", inline=False)
    embed.add_field(name=f"/createmuterole ", value="creates the mute role", inline=False)
    embed.add_field(name=f"/xp enable", value="enables the xp system.", inline=False)
    embed.add_field(name=f"/xp disable", value="disables the xp system.", inline=False)
    embed.add_field(name=f"/xp set <user> <amount>", value="sets the xp amount for a given user.", inline=False)
    embed.add_field(name=f"/xp add <user> <amount>", value="adds the given amount to a users xp.", inline=False)
    embed.add_field(name=f"/xp remove <user> <amount>", value="removes the given amount from a users xp.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)
bot.tree.add_command(help)

@app_commands.command(name='invite', description='Invite link.')
async def invite(interaction: discord.Interaction):
    await interaction.response.send_message(f'Invite link: https://discord.com/oauth2/authorize?client_id={bot.application_id}&permissions=8&scope=bot%20applications.commands', ephemeral=True)
bot.tree.add_command(invite)

# MUSIC STUFF

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        youtube_dl.utils.bug_reports_message = lambda: ''
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
        ffmpeg_options = {
            'options': '-vn',
        }
        ytdl = youtube_dl.YoutubeDL(ydl_opts)
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class SelectSong(discord.ui.Select):
    def __init__(self,options: dict):
        self.optionz = options['results']
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options['options'])
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=f"Now Playing {self.values[0]}!",ephemeral=True)
        url = 'https://youtube.com'
        for x in self.optionz:
            if x['title'] == self.values[0]:
                url += x['url_suffix']
        b = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if b != None:
            await interaction.guild.voice_client.disconnect()
        try:
            vc = await interaction.user.voice.channel.connect()
        except:
            await interaction.response.send_message(f"{interaction.message.author.mention}, you not in a voice channel.", ephemeral=True)
            return
        audio = await YTDLSource.from_url(url=url, loop=bot.loop, stream=True)
        vc.play(audio)
        while vc.is_playing():
            await asyncio.sleep(.1)
        vc.stop()
        await vc.disconnect()
        


class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, options: dict):
        super().__init__(timeout=timeout)
        self.add_item(SelectSong(options=options))

@app_commands.command(name='play', description='plays a song from youtube.')
async def play(interaction: discord.Interaction, song: str):
    message = await interaction.response.send_message('Searching...', ephemeral=True)
    f = False    
    results = YoutubeSearch(song, max_results=10).to_json()
    results = json.loads(results)
    results = results['videos']
    options = []
    for i in results:
        options.append(discord.SelectOption(label=i['title'], description=f'By {i["channel"]}', emoji='🎧'))
    options = {'options': options, 'results': results}
    view = SelectView(options=options)
    await interaction.edit_original_message(content='Select a song to play:',view=view)
bot.tree.add_command(play)


# xp stuff
@bot.listen('on_message')
async def on_message(message):
    if message.author.bot:
        await bot.process_commands(message)
        return
    if message.guild is None:
        await bot.process_commands(message)
        return
    with open(f'Files/{message.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] != None:
            data['xp'][str(message.author.id)] += 1
            with open(f'Files/{message.guild.id}.json', 'w') as f:
                json.dump(data, f)
            try:
                z = open(f'Files/{message.guild.id}.json', 'r')
                data2 = json.load(z)
                if data == data2:
                    await bot.process_commands(message)
                    return
            except:
                os.remove(f'Files/{message.guild.id}.json')
                json.dump(data, f)
                await bot.process_commands(message)
                return
        else:
            await bot.process_commands(message)
            return
    
@app_commands.command(name='stats', description='gets a users stats.')
async def stats(interaction: discord.Interaction, user: discord.Member = None):
    if user == None:
        user = interaction.user
    embed = discord.Embed(title=f'{user.name} Stats', color=0x00ff00)
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] != False:
            embed.add_field(name='XP', value=data['xp'][str(user.id)])
        else:
            embed.add_field(name='XP', value=0)
    await interaction.response.send_message(embed=embed)
bot.tree.add_command(stats)

xp = discord.app_commands.Group(name='xp', description='xp related commands.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='disable', description='disables the xp system.')
async def disable(interaction: discord.Interaction):
    await interaction.response.send_message('Disabling XP...')
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        data['xp'] = False
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.edit_original_message(content='XP is now disabled!')
@disable.error
async def disable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='enable', description='enables the xp system.')
async def enable(interaction: discord.Interaction):
    await interaction.response.send_message('Enabling XP...\n this may take a while on some servers.')
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        data['xp'] = {}
        for user in interaction.guild.members:
            data['xp'][user.id] = 0
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.edit_original_message(content='XP is now enabled!')
@enable.error
async def enable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')

@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='set', description='sets a users xp.')
async def set(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        data['xp'][str(user.id)] = amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(f'{user.mention}\'s xp has been set to {amount}.')
@set.error
async def set_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='add', description='adds to a users xp.')
async def add(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        data['xp'][str(user.id)] += amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(f'{user.mention}\'s xp has been added to {amount}.')
@add.error
async def add_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='remove', description='removes from a users xp.')
async def remove(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        data['xp'][str(user.id)] -= amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(f'{user.mention}\'s xp has been removed from {amount}.')
@remove.error
async def remove_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')

bot.tree.add_command(xp)

bot.run(token)
