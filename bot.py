Version = '3.0.1'
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
from discord_together import DiscordTogether
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
        if data['xp'] == True:
            if member.id not in data['xp']:
                data['xp'][member.id] = 0
                with open(f'./Files/{member.guild.id}.json', 'w') as f:
                    json.dump(data, f)

@bot.event
async def on_ready():
    bot.togetherControl = await DiscordTogether(token)
    for a in bot.guilds:
        if not os.path.exists(f'./Files/{a.id}.json'):
            with open(f'./Files/{a.id}.json', 'w') as f:
                x = {"MuteRole":False,"xp":False}
                json.dump(x, f)
    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        with open(f'./Files/{guild.id}.json', 'r') as f:
            try:
                x = json.load(f)
            except:
                x = {"MuteRole":False,"xp":False,"bannedwords":False}
                with open(f'./Files/{guild.id}.json', 'w') as f:
                    json.dump(x, f)
            if 'MuteRole' not in x:
                x['MuteRole'] = False
                with open(f'./Files/{guild.id}.json', 'w') as f:
                    json.dump(x, f)
            if 'xp' not in x:
                x['xp'] = False
                with open(f'./Files/{guild.id}.json', 'w') as f:
                    json.dump(x, f)
            if 'bannedwords' not in x:
                x['bannedwords'] = False
                with open(f'./Files/{guild.id}.json', 'w') as f:
                    json.dump(x, f)
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
    if member == bot.user:
        await interaction.send('No.')
        return
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

purge = discord.app_commands.Group(name='purge', description='Purges messages.')
@discord.app_commands.checks.has_permissions(administrator=True)
@purge.command(name='channel', description='Purges messages from a channel.')
async def purge_channel(interaction: discord.Interaction, channel: discord.TextChannel = None, amount: int = 0,):
    if channel is None:
        channel = interaction.channel
    if amount == 0:
        view=Buttons2()
        await interaction.response.send_message('This will purge all messages, are you sure?',view=view,ephemeral=True)
        time = 0
        while view.show() is None:
            time += 1
            if time == 200:
                await interaction.edit_original_message(content='Purge cancelled.',view=None)
                return
            await asyncio.sleep(.1)
        if view.show() == False:
            await interaction.edit_original_message(content='Purge cancelled.',view=None)
            return
        await channel.purge()
        if channel == interaction.channel:
            await interaction.followup.send(f'Purged all messages from channel {channel}.',ephemeral=True)
        else:
            await interaction.edit_original_message(content=f'Purged all messages from channel {channel}.',view=None)
    else:
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f'Purged {amount} messages in {channel}',ephemeral=True)
@purge_channel.error
async def purge_channel_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message('admin privileges are required to use this command.',ephemeral=True)
@discord.app_commands.checks.has_permissions(administrator=True)
@purge.command(name='user', description='Purges messages from a user.')
async def purge_user(interaction: discord.Interaction, user: discord.Member, amount: int = 0):
    if user == bot.user:
        await interaction.response.send_message('No.',ephemeral=True)
        return
    if amount == 0:
        view=Buttons2()
        await interaction.response.send_message(f'This will purge all messages from {user.mention}, are you sure?',view=view,ephemeral=True)
        time = 0
        while view.show() is None:
            time += 1
            if time == 300:
                await interaction.edit_original_message(content='Purge cancelled.',view=None)
                return
            await asyncio.sleep(.1)
        if view.show() == False:
            await interaction.edit_original_message(content='Cancelled.',view=None)
            return
        await interaction.channel.purge(check=lambda m: m.author == user)
        await interaction.edit_original_message(content=f'Purged all messages from {user.mention}.',view=None)
    else:
        await interaction.channel.purge(check=lambda m: m.author == user, limit=amount)
        await interaction.response.send_message(f'Purged {amount} messages from {user.mention}',ephemeral=True)
@purge_user.error
async def purge_user_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message('admin privileges are required to use this command.',ephemeral=True)


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
    try:
        await interaction.edit_original_message(content='Select a song to play:',view=view)
    except:
        await interaction.edit_original_message(content='An error occured. Please try again.')

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

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180, num: str):
        self.num = num
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Yes",style=discord.ButtonStyle.green)
    async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        bot.musicqueue[interaction.guild.id].remove(self.num)
        await interaction.response.edit_message(content=f"Removed {self.num} from queue.")
    @discord.ui.button(label="No",style=discord.ButtonStyle.red)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.edit_message(content='Cancelled.',)

@music.command(name='delqueue', description='removes a song from the queue.')
async def delqueue(interaction: discord.Interaction, song: str):
    if bot.musicqueue[interaction.guild.id] == []:
        await interaction.response.send_message("No songs in queue.", ephemeral=True)
        return
    songs = []
    for a in bot.musicqueue[interaction.guild.id]:
        if song in a:
            songs.append(a)
    view = Buttons(num=songs[0])
    interaction.response.send_message(f"would you ike to remove {songs[0]} from the queue?", view=view)

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
            if user.id != bot.user.id:
                embed.add_field(name='XP', value=data['xp'][str(user.id)])
            else:
                embed.add_field(name='XP', value='∞')
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

@app_commands.command(name='games', description='plays a party game')
async def games(interaction: discord.Interaction, game: typing.Literal['youtube', 'poker', 'chess', 'betrayal', 'fishing', 'letter-league', 'word-snack', 'sketch-heads', 'spellcast', 'awkword', 'checkers', 'blazing-8s', 'land-io', 'putt-party']):  
    if interaction.user.voice is None:
        await interaction.response.send_message('You must be in a voice channel to play a game.',ephemeral=True)
        return
    link = await bot.togetherControl.create_link(interaction.user.voice.channel.id, game)
    await interaction.response.send_message(f"click the link to play!\n{link}", suppress_embeds=True, ephemeral=True)
bot.tree.add_command(games)

@bot.listen('on_message')
async def on_message(message):
    if message.author == bot.user:
        return
    with open(f'Files/{message.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] == False:
            return
        p = []
        for word in data['bannedwords']:
            if word in message.content:
                p.append(word)
        if len(p) != 0:
            try:
                await message.delete()
            except:
                return
            string = ''
            for word in p:
                string += f'{word}{", " if word != p[len(p)-1] else ""} '
            await message.channel.send(f'{message.author.mention}, please refrain from saying the following word{"s" if len(p) > 0 else ""}: {string}')

banwords = discord.app_commands.Group(name='banwords', description='manages banned words.')
@discord.app_commands.checks.has_permissions(administrator=True)
@banwords.command(name='set', description='sets the banword list to a custom list from a url.')
async def URL(interaction: discord.Interaction, url: str):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        words = []
        if await checkurl(url=url) != True:
            await interaction.response.send_message('That is not a valid url. Please ensure that the url points to a text file, and all words are seperated with a newline.',ephemeral=True)
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                for line in str(await r.text()).split('\n'):
                    if line == '':
                        continue
                    words.append(line.strip())
        with open('banwords.txt', 'w') as f:
            for word in words:
                f.write(f'{word}\n')
        view = Buttons2()
        await interaction.response.send_message('Does this look correct?',ephemeral=True,view=view,file=discord.File('banwords.txt'))
        os.remove('banwords.txt')
        time = 0
        while view.show() == None:
            await asyncio.sleep(.1)
            time += .1
            if time == 30:
                await interaction.edit_original_message(content='You took too long to respond, please try again.',view=None,attachments=[])
                return
        if view.show() == True:
            data['bannedwords'] = words
            with open(f'Files/{interaction.guild.id}.json', 'w') as f:
                json.dump(data, f)
                await interaction.edit_original_message(content=f'The banword list has been set, use `/banwords show` to show it.', view=None,attachments=[])
        else:
            await interaction.edit_original_message(content='Cancelled.',view=None,attachments=[])

@discord.app_commands.checks.has_permissions(administrator=True)
@banwords.command(name='add', description='adds a word to the banned words list.')
async def add(interaction: discord.Interaction, word: str):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] == False:
            await interaction.response.send_message('Banned words are not enabled!')
            return
        if word in data['bannedwords']:
            await interaction.response.send_message(f'{word} is already banned.')
            return
        data['bannedwords'].append(word)
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(f'{word} has been banned.')
@add.error
async def add_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')
@discord.app_commands.checks.has_permissions(administrator=True)
@banwords.command(name='remove', description='removes a word from the banned words list.')
async def remove(interaction: discord.Interaction, word: str):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] == False:
            await interaction.response.send_message('Banned words are not enabled!')
            return
        if word not in data['bannedwords']:
            await interaction.response.send_message(f'{word} is not banned.')
            return
        data['bannedwords'].remove(word)
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(f'{word} has been unbanned.')
@remove.error
async def remove_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')

class Buttons2(discord.ui.View):
    def __init__(self, *, timeout=180,):
        self.num = None
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Yes",style=discord.ButtonStyle.green)
    async def blurple_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.num = True
    @discord.ui.button(label="No",style=discord.ButtonStyle.red)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        self.num = False
    def show(self):
        return self.num

@discord.app_commands.checks.has_permissions(administrator=True)
@banwords.command(name='enable', description='enables banned words.')
async def enable(interaction: discord.Interaction):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] != False:
            await interaction.response.send_message('Banned words are already enabled!', ephemeral=True)
            return
        data['bannedwords'] = []
        view = Buttons2()
        await interaction.response.send_message('would you like to use a preset banwords list?', view=view, ephemeral=True)
        time = 0
        while view.show() is None:
            if time == 300:
                await interaction.edit_original_message('Timed out.')
                return
            await asyncio.sleep(.1)
            time += .1
        if view.show() == False:
            with open(f'Files/{interaction.guild.id}.json', 'w') as f:
                json.dump(data, f)
            await interaction.edit_original_message(content='Banned words are now enabled, but no words have been added. Use `/banwords` to manage them.',view=None)
            return
        if view.show() == True:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://www.cs.cmu.edu/~biglou/resources/bad-words.txt') as resp:
                    p = await resp.text()
                    f = []
                    for word in p.split('\n'):
                        if word != '':
                            f.append(word.strip())
                    with open(f'Files/{interaction.guild.id}.json', 'w') as z:
                        data['bannedwords'] = f
                        json.dump(data, z)
                        await interaction.edit_original_message(content='Banned words are now enabled using the default list (taken from https://www.cs.cmu.edu/~biglou/resources/bad-words.txt). Use `/banwords` to manage them.',view=None)
                        return
@enable.error
async def enable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')

@banwords.command(name='disable', description='disables banned words.')
async def disable(interaction: discord.Interaction):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] == False:
            await interaction.response.send_message('Banned words are already disabled!', ephemeral=True)
            return
        data['bannedwords'] = False
        with open(f'Files/{interaction.guild.id}.json', 'w') as f:
            json.dump(data, f)
            await interaction.response.send_message(content='Banned words are now disabled.')
@disable.error
async def disable_error(interaction: discord.Interaction, error: Exception):
    await interaction.response.send_message(f'{interaction.user.mention}, You are not an admin on {interaction.guild.name}.')

@banwords.command(name='show', description='shows banned words.')
async def show(interaction: discord.Interaction):
    with open(f'Files/{interaction.guild.id}.json', 'r') as f:
        data = json.load(f)
        if data['bannedwords'] == False:
            await interaction.response.send_message('Banned words are not enabled!', ephemeral=True)
            return
        p = ''
        if data['bannedwords'] == []:
            await interaction.response.send_message('No words have been banned.', ephemeral=True)
            return
        if len(data['bannedwords']) < 21:
            for word in data['bannedwords']:
                p += f'{word}{", " if word != data["bannedwords"][len(data["bannedwords"])-1] else ""}'
            await interaction.response.send_message(f'Banned words: {p}', ephemeral=True)
        else:
            for word in data['bannedwords']:
                p += f'{word}{", " if word != data["bannedwords"][len(data["bannedwords"])-1] else ""}'
            with open('banlist.txt', 'w') as f:
                f.write(p)
            await interaction.response.send_message('Banned words:', file=discord.File('banlist.txt'), ephemeral=True)
            os.remove('banlist.txt')

bot.tree.add_command(banwords)

bot.run(token)
