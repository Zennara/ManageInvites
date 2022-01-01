#ManageInvites, by Zennara#8377

#imports
import os
import keep_alive
import discord
import asyncio
import json
import requests
from replit import db
import DiscordUtils

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

#check invites and compare
invites = {}
last = ""
    

@client.event
async def on_ready():
  print("\nManageInvites Ready\n")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your invites"))

@client.event
async def on_member_join(member):
  inviter = await tracker.fetch_inviter(member) # inviter is the member who invited
  print(inviter)

@client.event
async def on_guild_join(guild):
  if guild.id not in dict(db).keys():
    db[str(guild.id)] = {}

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))