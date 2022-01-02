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

  #help command
  if messagecontent == prefix + 'help':
    embed = discord.Embed(color=0xFFFFFF, description="These are all the available commands. The prefix is `"+prefix+"`. You can change this at any time with `"+prefix+"prefix <newPrefix>`.\n")
    embed.set_author(name=client.user.name + " Help")
    embed.add_field(name="`"+prefix+ "invites [member]`", value="Shows how many invites the user has", inline=False)
    embed.add_field(name="`"+prefix+ "leaderboard`", value="Shows the invites leaderboard", inline=False)
    embed.add_field(name="`"+prefix+ "edit <invites|leaves> <amount> [member]`", value="Set invites or leaves of a user", inline=False)
    embed.add_field(name="`"+prefix+ "addirole <invites> <roleID>`", value="Add a new invite role reward", inline=False)
    embed.add_field(name="`"+prefix+ "delirole <invites> <roleID>`", value="Delete an invite role reward", inline=False)
    embed.add_field(name="`"+prefix+ "iroles`", value="Display all invite role rewards", inline=False)
    embed.add_field(name="`"+prefix+ "fetch invites`", value="Fetch all previous invites", inline=False)
    embed.set_footer(text="________________________\n<> Required | [] Optional\nMade By Zennara#8377")
    await message.channel.send(embed=embed)

  if messagecontent.startswith(prefix + 'invites'):
    #get user (member object)
    isInGuild = False
    minusMessageContent = message.content.replace("<","").replace(">","").replace("@","").replace("!","")
    if (messagecontent == prefix + 'invites'):
      user = message.author
      isInGuild = True
    else:
      dbUser = None
      #get db user
      if str(minusMessageContent[-18:]) in db[str(message.guild.id)]:
        dbUser = db[str(message.guild.id)][str(minusMessageContent[-18:])]
      else:
        embed = discord.Embed(color=0xFF0000, description="Invalid user or user has no invites.")
        embed.set_author(name="Error")
        await message.channel.send(embed=embed)
        return
      #get actual member
      if message.guild.get_member(int(minusMessageContent[-18:])) != None:
        user = message.guild.get_member(int(minusMessageContent[-18:]))
        isInGuild = True
    #get vars
    if isInGuild:
      Name = user.name + "#" + str(user.discriminator)
      Pfp = user.avatar_url
      Invites = db[str(message.guild.id)][str(user.id)][2]
      Leaves = db[str(message.guild.id)][str(user.id)][3]
      inviterUser = db[str(message.guild.id)][str(user.id)][1]
      joinCode = db[str(message.guild.id)][str(user.id)][0]
    else:
      Name = "<@"+str(minusMessageContent[-18:])+">"
      Pfp = ""
      Invites = db[str(message.guild.id)][str(minusMessageContent[-18:])][2]
      Leaves = db[str(message.guild.id)][str(minusMessageContent[-18:])][3]
      inviterUser = db[str(message.guild.id)][str(minusMessageContent[-18:])][1]
      joinCode = db[str(message.guild.id)][str(minusMessageContent[-18:])][0]
    totalInvites = Invites - Leaves
    #check for invite code and inviter
    print(4)
    print(joinCode + "|")
    if joinCode != "":
      print(0)
      getMember = message.guild.get_member(int(inviterUser))
      if getMember != None:
        print(1)
        text = getMember.name + "#" + str(getMember.discriminator)
      else:
        print(2)
        text = "<@"+str(inviterUser)+">"
      addition = "\nInvited by: " + text + " with code **"+joinCode+"**"
    else:
      addition = ""
    embed = discord.Embed(color=0x00FF00, description="User has **" + str(totalInvites) + "** invites! (**" + str(Invites) + "** regular, **-" + str(Leaves) + "** leaves)"+addition)
    if isInGuild:
      embed.set_author(name="@" + Name, icon_url=Pfp)
    else:
      embed = discord.Embed(color=0x00FF00, description=Name+"\nUser has **" + str(totalInvites) + "** invites! (**" + str(Invites) + "** regular, **-" + str(Leaves) + "** leaves)"+addition)
    await message.channel.send(embed=embed)


@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "i/"}



client.loop.create_task(getInvites())

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))