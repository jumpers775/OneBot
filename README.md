# onebot
Discord Evererything Bot

# [Invite link](https://discord.com/oauth2/authorize?client_id=863282370319876127&permissions=8&scope=bot%20applications.commands)
To use this link with your own bot, just replace the first set of numbers in the url with your bots bot id

# **Instructions for new bot**
First, install the dependencies using `python3 -m pip install discord json` (note that as of release the latest discord stable does not include slashes and you will need to install it with `python3 -m pip install -U git+https://github.com/Rapptz/discord.py`), then clone the github or unzip the latest release to an empty folder of your choosing. next, run the bot with `python3 bot.py`. Input your bots token and the bot will run. 


# **Instructions for old bot**
Note that the old bot currently has more features, but does not use slash commands, and is quite outdated. It may stop working at a later date.

To use this follow the below guide to install the dependencies, follow the wizard on first run, and then enabling member intents on the dashboard. 
use $help for a list of commands (replace $ with your chosen prefix). The bots role must be set above all of the non-mod roles, and it requires admin to make and manage roles/channels.

**DEPENDS:**
To run the bot you must first clone this by eityher downloading zip or running `git clone https://github.com/jumpers775/OneBot && cd Onebot`, then install python, and discord.py. python can be downloaded from python.org (or your distros package manager on linux/unix systems). install pip (`python3 -m ensurepip`) and then run `python3 -m pip install aiohttp discord youtube_dl ffmpeg youtube-search-python PyNaCl python-dotenv`. ensure discord.py version is 12.5.3. once these are installed the bot can be run from the terminal with the command `python oldbot.py`. make sure the bot is running when you invite it to a server so it can do first time setup. This supports windows, unix based OSes, and linux.

