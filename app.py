import datetime
import urllib.request
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import os  
from os import environ, path
from dotenv import load_dotenv

client = commands.Bot()
laststatus = -1

if(path.exists('bot.env')):
    try:
        load_dotenv(dotenv_path='bot.env')
        # settings
        Discord_bot_token = environ.get('discord_bot_token')            
        miner_ip = environ.get('miner_ip')
    except Exception as e:
        pass

else: 
    Discord_bot_token = str(os.environ['discord_bot_token'])


@client.event
async def on_ready():
    update_status.start()
    print('Status update loop initiated.')
    print('GarageBot v0.33 Online.')

@tasks.loop(minutes=10)
async def update_status():
    free = 0
    debug = False
    total = 1623 + 1259 + 1852 + 1241 + 1284 + 1231 + 1007
    updated = False

    parking = urllib.request.urlopen('https://secure.parking.ucf.edu/GarageCount/').read()
    soup = BeautifulSoup(parking, features="lxml")

    # Scrape occupied spots from website by searching for <strong>
    # (it just happens that the spots are some of the only ones)
    for item in soup.find_all('strong'):
        # Exclude the <strong> non-integer messages at the bottom
        try:
            free += float(item.string)
        except ValueError:
            if debug:
                print("Excluded string: \"" + item.string + "\"")

    global laststatus

    if round(free/total, 2) < 0.20 and laststatus != 0:
        await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name='< 20% Free - :['),)
        laststatus = 0
        updated = True
    elif round(free/total, 2) < 0.45 and laststatus != 1:
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name='< 45% Free :|'))
        laststatus = 1
        updated = True
    elif laststatus != 2:
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name='im alive ig'))
        laststatus = 2
        updated = True
    else:
        updated = False

    currtime = datetime.datetime.now()
    if updated == True:
        print(f'Updated status at {currtime.strftime("%c")} EST')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases=['free', 'spot', 'space', 'full'])
async def spots(ctx):
    debug = False

    currtime = datetime.datetime.now()
    print(f'Request made at {currtime.strftime("%c")} EST')

    total_spots = [1623, 1259, 1852, 1241, 1284, 1231, 1007]
    scraped_spots = []

    parking = urllib.request.urlopen('https://secure.parking.ucf.edu/GarageCount/').read()
    soup = BeautifulSoup(parking, features="lxml")

    # Scrape occupied spots from website by searching for <strong>
    # (it just happens that the spots are some of the only ones)
    for item in soup.find_all('strong'):
        # Exclude the <strong> non-integer messages at the bottom
        try:
            scraped_spots.append(int(item.string))
        except ValueError:
            if debug:
                print("Excluded string: \"" + item.string + "\"")

    message = (
        f'```UCF PARK*cough*ING STATUS as of {currtime.strftime("%c")}\n'
        f'Garage A Free Spaces: {scraped_spots[0]}/{total_spots[0]}\t --- {int(float(scraped_spots[0]/total_spots[0]) * 100)}% Free\n'
        f'Garage B Free Spaces: {scraped_spots[1]}/{total_spots[1]}\t --- {int(float(scraped_spots[1]/total_spots[1]) * 100)}% Free\n'
        f'Garage C Free Spaces: {scraped_spots[2]}/{total_spots[2]}\t --- {int(float(scraped_spots[2]/total_spots[2]) * 100)}% Free\n'
        f'Garage D Free Spaces: {scraped_spots[3]}/{total_spots[3]}\t --- {int(float(scraped_spots[3]/total_spots[3]) * 100)}% Free\n'
        f'Garage H Free Spaces: {scraped_spots[4]}/{total_spots[4]}\t --- {int(float(scraped_spots[4]/total_spots[4]) * 100)}% Free\n'
        f'Garage I Free Spaces: {scraped_spots[5]}/{total_spots[5]}\t --- {int(float(scraped_spots[5]/total_spots[5]) * 100)}% Free\n'
        f'   Libra Free Spaces: {scraped_spots[6]}/{total_spots[6]}\t --- {int(float(scraped_spots[6]/total_spots[6]) * 100)}% Free```'
    )
    await ctx.send(message)
    currtime = datetime.datetime.now()
    print(f'Request honored at {currtime.strftime("%c")} EST')


client.run(settings.token)
