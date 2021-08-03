# bot.py
import os

import discord
from dotenv import load_dotenv
import random
from riotwatcher import LolWatcher
from datetime import datetime, timedelta
import asyncio
from math import floor

# Initialize the enviornment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv("CHANNEL_ID")
LOLAPI = os.getenv('LOL_API_KEY')

# Fetch the league of legends champions
lol_watcher = LolWatcher(LOLAPI)
versions = lol_watcher.data_dragon.versions_for_region('na1')
champions_version = versions['n']['champion']
current_champ_list = lol_watcher.data_dragon.champions(champions_version)
champs = list(current_champ_list["data"].keys())
rnd_champ = random.choice(champs)

# Initialize the events and msgs
ff_event = [
    f"OMFG OF COURSE THEY HAVE A {rnd_champ.upper()}... WHY WOULDN'T THEY HAVE A {rnd_champ.upper()}...",
    # "My dino hotpockies are done - brb!\n\nA summoner has disconnected.",
    # "I would easily be platnum if it wasn't for my team.",
    # "ADC GAP. GG.",
]
events = [ff_event]
num_events = len(events)

# Initialize the terminate messages
rnd_lane = random.choice(["top", "jung", "mid", "adc", "sup", "team"])
terminate_msgs = [
    f"{rnd_lane} diff... The enemy {rnd_champ} is {random.randint(10, 50)}\\0\\{random.randint(10, 50)}."
]

# Grab the current point score
with open("points.txt", 'r') as f:
    points = int(f.read())

# Initialize the start and stop times
# This will be overwritten at 'on_ready'
now = None
stop = None
td = timedelta(hours = 1)

# Initialize the /ff contributor list
ff_contribs = []
req_contribs = 4

# Initialize the discord bot
client = discord.Client()

@client.event
async def on_message(message):
    author = message.author

    # Ignore yourself mr. saltbot
    if author == client.user:
        return

    # Handle the pts command
    if '/pts' in message.content.lower():
        await message.channel.send(f"Your team has {points} points.")
        return None

    if '/champs' in message.content.lower():
        # Discord has some limitations so send it in two chunks...
        half_champs = floor(len(champs) / 2)
        analysis = [f"{champ}:\t Broken\n" for champ in champs[:half_champs]]
        msg = "".join(analysis)
        await message.channel.send(msg)

        analysis = [f"{champ}:\t Broken\n" for champ in champs[half_champs:]]
        msg = "".join(analysis)
        await message.channel.send(msg)
        return None

    # Handle the ff command
    if '/ff' in message.content.lower():
        if message.author not in ff_contribs:
            ff_contribs.append(message.author)
            await message.channel.send(f"{author} accepts the surrender request... wise move")
        else:
            await message.channel.send(f"wtf {author}, you already surrenderd.")
            return None

    if len(ff_contribs) >= req_contribs:
        # Add the points!
        new_points = points + 1
        with open("points.txt", 'w') as f:
            f.write(str(new_points))

        # Send the congratulation message
        await message.channel.send(f"Congratulations! You lost.\n\nOne point has been awarded.\nNew total points: {new_points}.")
        client.logout()
        exit()

async def terminate():
    # Wait for the client to be completely initialized
    await client.wait_until_ready()

    # Sleep until the end time
    await asyncio.sleep(td.seconds)

    # Grab the channel
    channel = client.get_channel(int(CHANNEL_ID))

    # Send the terminate message
    msg = random.choice(terminate_msgs)
    await channel.send(msg)
    client.logout()
    exit()

@client.event
async def on_ready():
    # Get the proper guild
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    # Grab a random event
    event_idx = random.randint(0, num_events - 1)

    # Grab a msg from within the random event
    msg = random.choice(events[event_idx])

    # Grab the channel
    channel = client.get_channel(int(CHANNEL_ID))

    # Grab the current time and compute the stop time
    now = datetime.now()
    stop = (now + td).strftime("%H:%M")

    # Append the message with the stop time and instructions
    msg = "\n\n" + msg + "\n\n"
    msg += f"Type /ff within the next {td.seconds//3600} hour ({stop}) to end this missery.\n\n"
    msg += f"One point will be awarded if more than {req_contribs} people agree to surrender.\n\n"
    msg += "Type /pts to see your team's current score.\n\n"
    msg += "Type /champs to see an in-depth analysis of the meta for each champion based on 200-years of game design experience."

    # Send the message!
    await channel.send(msg)

    # Create the sub task
    client.loop.create_task(terminate())

# Run the client
client.run(TOKEN)
