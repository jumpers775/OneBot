Version = '3.0.1b1'
import os
import ffmpeg
import math
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
            if x['xp'] != False:
                if len(guild.members) != len(x['xp']):
                    for member in guild.members:
                        if member.id not in x['xp']:
                            x['xp'][member.id] = 0
                    with open(f'./Files/{guild.id}.json', 'w') as f:
                        json.dump(x, f)
    bot.starttime = datetime.datetime.now()
    bot.musicqueue = {}
    for guild in bot.guilds:
        bot.musicqueue[guild.id] = []
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
@app_commands.command(name='purge', description='Purges messages from a channel.')
async def purge(interaction: discord.Interaction, member: discord.Member = None, amount: int = 1):
    if member is None:
        await interaction.response.send_message(f'Purging {amount} messages.')
        await interaction.channel.purge(limit=amount)
    else:
        await interaction.response.send_message(f'Purging {amount} messages from {member.mention}.')
        await interaction.channel.purge(limit=amount, check=lambda m: m.author == member)
bot.tree.add_command(purge)


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
    embed.add_field(name=f"/invite", value="gets the bot invite",inline=False)
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
        bot.musicqueue[interaction.guild.id].append(url)
        if not bot.musicqueue[interaction.guild.id][0] == url:
            return
        b = discord.utils.get(bot.voice_clients, guild=interaction.guild)
        if b != None:
            await interaction.guild.voice_client.disconnect()
        try:
            vc = await interaction.user.voice.channel.connect()
        except:
            await interaction.response.send_message(f"{interaction.message.author.mention}, you not in a voice channel.", ephemeral=True)
            return
        while not bot.musicqueue[interaction.guild.id] == []:
            url = bot.musicqueue[interaction.guild.id][0]
            audio = await YTDLSource.from_url(url=url, loop=bot.loop, stream=True)
            try:
                vc.play(audio)
            except:
                try:
                    vc.play(audio)
                except:
                    pass
            while vc.is_playing():
                await asyncio.sleep(.1)
            bot.musicqueue[interaction.guild.id].pop(0)
        vc.stop()
        await vc.disconnect()
        


class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180, options: dict):
        super().__init__(timeout=timeout)
        self.add_item(SelectSong(options=options))
music = discord.app_commands.Group(name='music', description='music related commands.')

@music.command(name='play', description='plays a song from youtube.')
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

#stop playing audio
@music.command(name='stop', description='stops the audio.')
async def stop(interaction: discord.Interaction):
    bot.musicqueue[interaction.guild.id] = []
    b = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if b != None:
        await interaction.guild.voice_client.disconnect()
    await interaction.response.send_message("Stopped playing audio.", ephemeral=True)

@music.command(name='showqueue', description='shows the current queue.')
async def showqueue(interaction: discord.Interaction):
    if bot.musicqueue[interaction.guild.id] == []:
        await interaction.response.send_message("No songs in queue.", ephemeral=True)
        return
    songs = []
    youtube_dl_opts = {}
    for a in bot.musicqueue[interaction.guild.id]:
        with youtube_dl.YoutubeDL(youtube_dl_opts) as ydl:
            info_dict = ydl.extract_info(a, download=False)
            video_title = info_dict.get('title', None)
            songs.append(f'{video_title}\n')
    await interaction.response.send_message(f"Songs in queue: {songs}", ephemeral=True)
bot.tree.add_command(music)

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
        if data['xp'] != False:
            data['xp'][str(message.author.id)] += 1
            p = int(data['xp'][str(message.author.id)])/100
            if p.is_integer():
                await message.add_reaction('🎉')
                #get role for level p
                try:
                    role = discord.utils.get(message.guild.roles, name=f'level {p}')
                except:
                    role = await message.guild.create_role(name=f'level {p}')
                await message.author.add_role(role)
                await message.author.remove_role(discord.utils.get(message.guild.roles, name=f'level {p-1}'))
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
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] != False:
            await interaction.response.send_message('Disabling XP...')
            data['xp'] = False
            with open(f'Files/{interaction.guild.id}.json', 'w') as f:
                json.dump(data, f)
                await interaction.edit_original_message(content='XP is now disabled!')
        else:
            await interaction.response.send_message('XP is already disabled!')
@disable.error
async def disable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.message.author.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='enable', description='enables the xp system.')
async def enable(interaction: discord.Interaction):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] != False:
            await interaction.response.send_message('XP is already enabled!')
            return
        await interaction.response.send_message('Enabling XP...\n this may take a while on some servers.')
        data['xp'] = {}
        for user in interaction.guild.members:
            data['xp'][user.id] = 0
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.edit_original_message(content='XP is now enabled!')
@enable.error
async def enable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')

@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='set', description='sets a users xp.')
async def set(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        x = math.trunc(data['xp'][str(user.id)]/100)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        data['xp'][str(user.id)] = amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            p = int(data['xp'][str(user.id)])/100
            p = math.trunc(p)
            role = discord.utils.get(interaction.guild.roles, name=f'level {p}')
            if role is None:
                role = await interaction.guild.create_role(name=f'level {str(p)}')
            await user.add_roles(role)
            try:
                await user.remove_roles(discord.utils.get(interaction.guild.roles, name=f'level {x}'))
            except:
                pass
            await interaction.response.send_message(f'{user.mention}\'s xp has been set to {amount}.')

@set.error
async def set_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='add', description='adds to a users xp.')
async def add(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        x = math.trunc(data['xp'][str(user.id)]/100)
        data['xp'][str(user.id)] += amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            p = int(data['xp'][str(user.id)])/100
            p = math.trunc(p)
            role = discord.utils.get(interaction.guild.roles, name=f'level {p}')
            if role is None:
                role = await interaction.guild.create_role(name=f'level {str(p)}')
            await user.add_roles(role)
            try:
                await user.remove_roles(discord.utils.get(interaction.guild.roles, name=f'level {x}'))
            except:
                pass
            await interaction.response.send_message(f'{amount} has been added to {user.mention}\'s .')
@add.error
async def add_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@xp.command(name='remove', description='removes from a users xp.')
async def remove(interaction: discord.Interaction, user: discord.Member, amount: int):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['xp'] == False:
            await interaction.response.send_message('XP is not enabled!')
            return
        x = math.trunc(data['xp'][str(user.id)]/100)
        data['xp'][str(user.id)] -= amount
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            p = int(data['xp'][str(user.id)])/100
            p = math.trunc(p)
            role = discord.utils.get(interaction.guild.roles, name=f'level {p}')
            if role is None:
                role = await interaction.guild.create_role(name=f'level {str(p)}')
            await user.add_roles(role)
            try:
                await user.remove_roles(discord.utils.get(interaction.guild.roles, name=f'level {x}'))
            except:
                pass
            await interaction.response.send_message(f'{amount} has been removed from {user.mention}\'s xp .')
@remove.error
async def remove_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')

bot.tree.add_command(xp)

bot.run(token)
