# bot.py
# Version 2.1

import aiohttp
import asyncio
import csv
import datetime
import discord
import os
import psutil
import random
import requests
import re
import subprocess
import time

from dotenv import load_dotenv
from discord import Intents
from discord.ext import commands
from requests import get

#Memory Leak Fix
for process in psutil.process_iter(attrs=['pid', 'name']):
    if process.info['name'].lower() == "koboldcpp.exe".lower():
        print(f"Terminating {process.info['name']} (PID: {process.info['pid']})")
        psutil.Process(process.info['pid']).terminate()  # Graceful termination
            # Use .kill() instead if you want to forcefully stop the process


intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.members = False

#Discord Tokens
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Kobold API
subprocess.Popen(["koboldcpp.exe", "--config", "Kobold_default.kcpps", "--quiet"],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
rate = 0.1 #rate that DB will respond to any message between 0 and 1

API_URL = "http://localhost:5001/api/v1/generate"

#Bot Params

bot = commands.Bot(command_prefix='$',intents=intents)

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

    #get when last scrape occurred
    scrape_time = os.path.getmtime('anime_data.csv')
    scrape_datetime = datetime.datetime.fromtimestamp(scrape_time)
    scrapetime = scrape_datetime.strftime('%m-%d-%Y %H:%M')
    print(f"Last modified time: {scrapetime}")


    
    print(str(ctx.author) + " used $update")
    ctx = bot.get_channel(1130364127727063171) #the-description-beta
    await ctx.purge() #add limit=100 to only delete 100 messages

    await ctx.send("**Last Scraped: " + str(scrapetime) + " Central Time**\n")
    
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

                            if len(str(lines[newline_start:newline_end])) > 2000:
                                newline_end -= 1
                            else:
                                message = "\n".join(lines[newline_start:newline_end])
                                if newline_end < newline_total:
                                    if str(lines[newline_end-1]).strip().isspace() or str(lines[newline_end-1]).strip() == "":
                                        print("true")
                                        newline_end -= 2
                                        message = "\n".join(lines[newline_start:newline_end])
                                
                                await ctx.send(message)
                                newline_start = newline_end
                                newline_end = newline_total
                                if newline_start >= newline_total:
                                    break


                    else:
                        await ctx.send(urls)
                        
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
    print(str(ctx.author) + " used $scrape")
    await ctx.send("Performing backflip for episode information, please wait...")
    subprocess.run(['python', 'LinkGenv6.py'])
    await ctx.send("Backflip complete.")

@bot.command()
async def scrapedoot(ctx):
    '''
    : scrapes for the new season then runs $update but with more doot
    '''
    print(str(ctx.author) + " used $scrapedoot")
    await scrape(ctx)
    await update(ctx)

    
@bot.command()
async def watch(ctx, *args):
    '''
    : updates the anime_data.csv watched column for a show
    '''
    print(str(ctx.author) + " used $watch")

    cancel = False

    input_title = ""
    input_watched = ""
    try:
        input_title = ' '.join(map(str, args[:-1]))
    except:
        print("invalid input_title")
        cancel = True

    try:
        input_watched = str(args[-1])
    except:
        print("invalid input_watched")
        cancel = True
                
    if cancel == False:

        url = []        #0
        title = []      #1
        watched = []    #2
        tagline = []    #3
        
        
        info = [url, title, watched, tagline]

        output_list = []

        with open('anime_data.csv', 'r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                url.append(row[0].strip())       # URL
                title.append(row[1].strip())     # Title
                watched.append(row[2].strip())   # Watched
                tagline.append(row[3].strip())   # Tagline

            ###Handle Watch Function
            index = -1
            try:
                print("debug 0")
                print(input_title)
                print(input_watched)
                print(title)
                index = title.index(input_title)
                print("debug 1")
                watched[index] = input_watched
                print("debug 2")
            except:
                print("error with index")
            
            for x in range(len(title)): #for each item
                output_list.append(str(info[0][x]) +","+ str(info[1][x]) +","+ str(info[2][x]) +","+ str(info[3][x]))

            rows = []
            with open('anime_data.csv', 'w', newline='') as file:
                csv_writer = csv.writer(file, delimiter=',')
                output_list.sort(key=lambda x: x.split(',')[1].lower())
                for row in output_list:
                    rows = row.split(',')
                    csv_writer.writerow(rows)

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
    
#@bot.command()
async def history(channel, limit):
    """Fetches and prints the last `limit` messages in the channel"""
    print(f"Fetching last {limit} messages from #{channel}...\n")  # Use channel directly

    messages = [msg async for msg in channel.history(limit=limit)]  # Use channel directly
    
    # Format messages, replace 'Description Bot' with 'DB:'
    formatted_messages = "\n".join(
        f"DB: {msg.content}" if msg.author == bot.user else f"{msg.author}: {msg.content}" 
        for msg in reversed(messages)
    )
    
    print(formatted_messages)  # Print formatted output
    return formatted_messages


@bot.event
async def on_message(message):
    
    # Check if the message starts with the bot's command prefix
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    if not message.author == bot.user:
        chance = random.random()
        print(str(chance))
        if chance <= rate or re.findall(r"(?i)\bDB\b\W*", str(message.content)) or re.findall(r"(?i)\bDescription Bot\b\W*", str(message.content)) or message.content.startswith('!!'):
            if chance <= rate:
                print("chance met, responding")
            elif re.findall(r"(?i)\bDB\b\W*", str(message.content)):
                print("DB mentioned, responding")
            elif re.findall(r"(?i)\bDescription Bot\b\W*", str(message.content)):
                print("Description Bot mentioned, responding")
            elif message.content.startswith('!!'):
                print("!! used, responding")
                            
            response = await llm_response(message.channel, message.author)
            await message.channel.send(response)

# Chat function
async def llm_response(channel, user):
    chat_history = str(await history(channel, 10))
       
    payload = {
        "n": 1,
        "max_context_length": 4096,
        "max_length": 240,
        "rep_pen": 1.07,
        "temperature": 0.75,
        "top_p": 0.92,
        "top_k": 100,
        "sampler_order": [6, 0, 1, 3, 4, 2, 5],
        "trim_stop": True,
        "bypass_eos": False,
        "stop_sequence": [f"\n{user}:", "\nDB:"],  # Dynamic stop sequences
        "memory": "DB Persona: slightly unfriendly, sarcastic, snarky, slightly unhelpful, never flirts, swears moderately, sometimes abbreviates long phrases\nDB is a female discord moderator for a discord server.\nDB does not use action tags, stage directions, or emotes.\nDB never references her own personality or tendencies in any way unless directly asked about them.\nDB is neutral to users who are homophobic, racist, misogynistic, or transphobic and will neither encourage or discourage such topics",
        "prompt": f"\n{chat_history}\nDB:",
    }

    print(payload)
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("results", [{}])[0].get("text", "").strip()
        else:
            return f"Error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to KoboldCpp API."


    

#async def get_chatgpt_response(CUSTOM_PROMPT, channel, message):
#    headers = {
#        'Authorization': f'Bearer {CHATGPT_API_KEY}',
#        'Content-Type': 'application/json',
#    }

    # Get the last # messages as additional context
#    previous_context = await get_context_from_previous_messages(channel, message)

#    context_list = []

#    context_list.append({'role': 'system', 'content': CUSTOM_PROMPT})
    
#    for line in previous_context.split("\n"):
#        if line.split(":")[0] == "Description Bot":
#            context_list.append({'role': 'system', 'content': line})
#        else:
#            context_list.append({'role': 'user', 'content': line})

#    context_list.append({'role' : 'user', 'content': message.content})
            
#    data = {
#        'model': 'gpt-3.5-turbo',
#        'messages': context_list,
#        'temperature': 0.8,
#        'max_tokens': 150,
#    }

#    async with aiohttp.ClientSession() as session:
#        try:
#            async with session.post(CHATGPT_API_URL, headers=headers, json=data) as response:
#                response_data = await response.json()
#                #print(response_data)  # Print the full API response for debugging purposes

#                if 'choices' in response_data and len(response_data['choices']) > 0:
#                    return response_data['choices'][0]['message']['content']
#                else:                    
#                    return (str(response_data).split(":")[2]).split("'")[1]
                    
#        except Exception as e:
#            print(f"Error during API request: {e}")
#            return "Oops! Something went wrong: {e}"


###################################
@bot.command()
async def server(ctx):
    '''
    : Tes only command
    '''
    print(str(ctx.author))
    if str(ctx.author) == "tesfallout#0":
        ip = get('https://api.ipify.org').text
        print('My public IP address is: {}'.format(ip))
        await ctx.send('My public IP address is: {}'.format(ip))
    else:
        print("This is a Tes only command")

bot.run(TOKEN)  # Where 'TOKEN' is your bot token
