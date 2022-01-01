#ManageInvites, by Zennara#8377

#imports
import os
import keep_alive
import discord
import asyncio
import json
import requests
from replit import db

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

async def getInvites():
  #wait for bot to be ready
  await client.wait_until_ready()
  #loop forever to check invites constantly across servers
  tmp = []
  invites = {}
  global invite
  while True:
    for guild in client.guilds:
      invs = await guild.invites()
      tmp = []
      for i in invs:
        for s in invites:
          if s[0] == i.code:
            if int(i.uses) > s[1]:
              #get inviter id
              invite = i
              break
        tmp.append(tuple((i.code, i.uses)))
      invites = tmp 
    await asyncio.sleep(0.1)



@client.event
async def on_ready():
  print("\nManageInvites Ready\n")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your invites"))


@client.event
async def on_member_join(member):
  #wait until getInvites() is done
  await asyncio.sleep(0.12)
  global invite
  print(invite.inviter.name)


@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  #get prefix
  prefix = db[str(message.guild.id)]["prefix"]

  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  messagecontent = message.content.lower()

@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "i/"}



client.loop.create_task(getInvites())

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))