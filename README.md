# onebot
Simple moderation discord bot

All that is required for use is adding a token from your own botto the token variable in the bot.py file, and enabling member intents on the dashboard. 
use $help for a list of commands (replace $ with your chosen prefix). The bots role must be set above all of the non-mod roles, and it requires admin to make and manage roles/channels.

To run the bot you must install python, and discord.py. python can be downloaded from python.org. install npm and then run npm install discord.py. discord.py version is 12.5.3. once these are installed the bot can be run from the terminal with the command python bot.py. this will not display any additional text in the window, but be assured its running. make sure the bot is running when you invite it to a server so it can do first time setup. This supports windows, unix based OSes, and linux.

list of required dependencies (should autoinstall, but if this fails manually install them. this can fail if you dont have pip installed, or if you are on a bsd or unix based system):
aiohttp
discord
youtube_dl
ffmpeg
youtube-search-python
PyNaCl

