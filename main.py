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
    await asyncio.sleep(1)



@client.event
async def on_ready():
  print("\nManageInvites Ready\n")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your invites"))


@client.event
async def on_member_join(member):
  #wait until getInvites() is done
  await asyncio.sleep(1.1)
  global invite

  print(invite.inviter.name)
  #add new member into db
  if str(member.id) not in db[str(member.guild.id)]:
    db[str(member.guild.id)][str(member.id)] = [str(invite.code),invite.inviter.id,0,0]
  #add invite to inviter
  #chcek if inviter in db
  if str(invite.inviter.id) not in db[str(member.guild.id)]:
    db[str(member.guild.id)][str(invite.inviter.id)] = ["",0,0,0]
  db[str(member.guild.id)][str(invite.inviter.id)][2] += 1


@client.event
async def on_member_remove(member):
  #add to leaves
  #chcek if left member is in db
  if str(member.id) in db[str(member.guild.id)]:
    #ensure there was inviter
    if db[str(member.guild.id)][str(member.id)][0] != "":
      #check if inviter is in db
      if str(db[str(member.guild.id)][str(member.id)][1]) not in db[str(member.guild.id)]:
        db[str(member.guild.id)][str(db[str(member.guild.id)][str(member.id)][1])]= ["",0,0,0]
      #add to inviter leaves
      db[str(member.guild.id)][str(db[str(member.guild.id)][str(member.id)][1])][3] += 1


@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  messagecontent = message.content.lower()

  if messagecontent == "i/clear":
    db[str(message.guild.id)] = {"prefix": "i/"}

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


@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "i/"}



client.loop.create_task(getInvites())

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))