# bot.py
# Version 2.0


import asyncio
import discord
import os
import random
import requests
import re
import subprocess
from datetime import date
from datetime import timedelta
from dotenv import load_dotenv
from discord.ext import commands
from requests import get

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='$')

admins = ["Tesfallout#3687","Oceansevan#4977"]

###
#admin messages
###        
@bot.event
async def on_ready():
    print("Description Bot V2 is online")

###
###list management
###

def get_urls():
    completed_process = subprocess.run(['python', 'urls.py'], capture_output=True, text=True)
    if completed_process.returncode == 0:
        return completed_process.stdout.strip()
    else:
        print("Error running the child script.")
        return None
    
@bot.command()
async def purge(ctx):
    '''
    : purges bot-test channel
    '''
    print(str(ctx.author) + " used $purge")
    
    if str(ctx.author) != "Tesfallout#3687":
        ctx = bot.get_channel(829855156900069397) #bot-test

    await ctx.channel.purge(limit=1000000)


@bot.command()
async def update(ctx):
    '''
    : updates the description
    '''
    print(str(ctx.author) + " used $update")
    ctx = bot.get_channel(1130364127727063171) #the-description-beta
    await ctx.purge() #add limit=100 to only delete 100 messages
    message=""
    
    with open("descriptionV2.txt") as f:
        for line in f:
            if line.strip("\n") == "----------generate urls----------":
                urls = get_urls()
                if urls:
                    if len(urls) > 2000:
                        lines = urls.split("\n")
                        newline_start = 0
                        newline_total = len(lines)
                        print(str(newline_total)) #####
                        newline_end = newline_total

                        while True:
                            print(len(str(lines[newline_start:newline_end])))#####
                            if len(str(lines[newline_start:newline_end])) > 2000 :
                                newline_end -= 1
                            else:
                                message = "\n".join(lines[newline_start:newline_end])
                                await ctx.send(message)
                                newline_start = newline_end + 1
                                newline_end = newline_total
                                if newline_start >= newline_total:
                                    break

                    else:
                        message = urls
                        await ctx.send(message)
                        
                    message = ""

            elif line.strip("\n") != "--------------------":
                message = message + line
            
            else:
                message = message + "--------------------"
                pinMe = await ctx.send(message)
                await pinMe.pin()
                message = ""
                await ctx.purge(limit=1)# deletes the pinned message
    f.close()


@bot.command()
async def updoot(ctx):
    '''
    : runs $update but with more doot
    '''
    print(str(ctx.author) + " used $updoot")
    await update(ctx)

@bot.command()
async def scrape(ctx):
    '''
    : scrapes for the new season
    '''
    await ctx.send("Fetching episode information, please wait...")
    subprocess.run(['python', 'scrape.py'])
    await ctx.send("Scrape complete.")
    
@bot.command()
async def fact(ctx, *args):
    '''
    : posts a random piece of trivia
    '''
    print(str(ctx.author) + " used $fact")
    #input handling
    arg = 0
    try:
        arg = int(args[0])
                
    except:
        arg = 0

    #finding the fact
    f = open("trivia.txt",'r', errors='ignore')
    lines = f.readlines()    

    if arg == 0:
        index=lines.index(random.choice(lines))
        await ctx.send(lines[index].strip("\n")+" (Fact #" +str(index+1)+")")

    else:
        try:
            await ctx.send(lines[arg-1].strip("\n"))
        except:
            await ctx.send("sorry, I don't have that fact yet")        
    f.close


@bot.command()
async def inspire(ctx):
    '''
    : Passes on hidden wisdom
    '''
    print(str(ctx.author) + " used $inspire")
    r = requests.get("https://inspirobot.me/api?generate=true")
    await ctx.send(r.text)
    

@bot.command()
async def server(ctx):
    '''
    : Tes only command
    '''
    if str(ctx.author) == "Tesfallout#3687":
        ip = get('https://api.ipify.org').text
        print('My public IP address is: {}'.format(ip))
        await ctx.send('My public IP address is: {}'.format(ip))
    else:
        print("This is a Tes only command")

bot.run(TOKEN)  # Where 'TOKEN' is your bot token
