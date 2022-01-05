#ManageInvites, by Zennara#8377

#imports
import os
import keep_alive
import discord
import asyncio
import json
import requests
from replit import db
import math
import random
import datetime

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
  print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
  print("No rate limit")

#declare client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

#async def getInvites():
  #wait for bot to be ready
#  await client.wait_until_ready()
  #loop forever to check invites constantly across servers
#  tmp = []
#  invites = {}
#  global invite
#  while True:
#    for guild in client.guilds:
#      invs = await guild.invites()
#      tmp = []
#      for i in invs:
#        for s in invites:
#          if s[0] == i.code:
#            if int(i.uses) > s[1]:
              #get inviter id
#              invite = i
#              await asyncio.sleep(1)
#              break
#        tmp.append(tuple((i.code, i.uses)))
#      invites = tmp

async def error(message, code):
  embed = discord.Embed(color=0xff0000, description=code)
  if random.randint(1,3) == 1:
    embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
  await message.channel.send(embed=embed)

def checkPerms(message):
  if message.author.guild_permissions.manage_guild:
    return True
  else:
    asyncio.create_task(error(message, "You do not have the valid permission: `MANAGE_GUILD`."))


invites = {}

@client.event
async def on_invite_create(invite):
  #write cache
  invites[invite.guild.id] = await invite.guild.invites()

@client.event
async def on_invite_delete(invite):
  #write cache
  invites[invite.guild.id] = await invite.guild.invites()

@client.event
async def on_ready():
  print("\nManageInvites Ready\n")
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your invites"))

  # Getting all the guilds our bot is in
  for guild in client.guilds:
    # Adding each guild's invites to our dict
    invites[guild.id] = await guild.invites()

def find_invite_by_code(invite_list, code): 
  # Simply looping through each invite in an
  # invite list which we will get using guild.invites()
  for inv in invite_list:
    # Check if the invite code in this element
    # of the list is the one we're looking for  
    if inv.code == code:       
      # If it is, we return it.      
      return inv

async def checkRewards(member):
  #check if in db
  if str(member.id) in db[str(member.guild.id)]:
    #add to invites
    for irole in db[str(member.guild.id)]["iroles"]:
      roleIDs = []
      for role in member.roles:
        roleIDs.append(str(role.id))
      if db[str(member.guild.id)][str(member.id)][2] - db[str(member.guild.id)][str(member.id)][3] >= db[str(member.guild.id)]["iroles"][irole]:
        await member.guild.get_member(member.id).add_roles(member.guild.get_role(int(irole)),reason="Invite Reward",atomic=True)
      elif str(member.guild.get_role(int(irole)).id) in roleIDs:
        await member.guild.get_member(member.id).remove_roles(member.guild.get_role(int(irole)),reason="Invite Reward",atomic=True)

@client.event
async def on_member_join(member):  
  invites_before_join = invites[member.guild.id]
  invites_after_join = await member.guild.invites()
  for invite in invites_before_join: 
    if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
      gotInvite = invite
      #print(f"Member {member.name} Joined")
      #print(f"Invite Code: {invite.code}")
      #print(f"Inviter: {invite.inviter}")
      invites[member.guild.id] = invites_after_join
      break

  #print(gotInvite.inviter.name)
  #add new member into db
  if str(member.id) not in db[str(member.guild.id)]:
    db[str(member.guild.id)][str(member.id)] = [str(gotInvite.code),gotInvite.inviter.id,0,0]
  #add invite to inviter
  #check if inviter in db
  if str(gotInvite.inviter.id) not in db[str(member.guild.id)]:
    db[str(member.guild.id)][str(gotInvite.inviter.id)] = ["",0,0,0]
  db[str(member.guild.id)][str(gotInvite.inviter.id)][2] += 1

  await checkRewards(member.guild.get_member(gotInvite.inviter.id))


@client.event
async def on_member_remove(member):
  #add to leaves
  #check if left member is in db
  if str(member.id) in db[str(member.guild.id)]:
    #ensure there was inviter
    if db[str(member.guild.id)][str(member.id)][0] != "":
      #check if inviter is in db
      if str(db[str(member.guild.id)][str(member.id)][1]) not in db[str(member.guild.id)]:
        db[str(member.guild.id)][str(db[str(member.guild.id)][str(member.id)][1])]= ["",0,0,0]
      #add to inviter leaves
      db[str(member.guild.id)][str(db[str(member.guild.id)][str(member.id)][1])][3] += 1
      await checkRewards(member.guild.get_member(int(db[str(member.guild.id)][str(member.id)][1])))
  #write cache
  invites[member.guild.id] = await member.guild.invites()


@client.event
async def on_message(message):
  #check for bots
  if message.author.bot:
    return

  #get random
  rand = True if random.randint(1,3) == 1 else False

  messagecontent = message.content.lower()

  if messagecontent == "i/clear":
    db[str(message.guild.id)] = {"prefix": "i/"}
    db[str(message.guild.id)]["iroles"] = {}

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
    embed.add_field(name="`"+prefix+ "leaderboard [page]`", value="Shows the invites leaderboard", inline=False)
    embed.add_field(name="`"+prefix+ "edit <invites|leaves> <amount> [member]`", value="Set invites or leaves of a user", inline=False)
    embed.add_field(name="`"+prefix+ "addirole <invites> <role>`", value="Add a new invite role reward", inline=False)
    embed.add_field(name="`"+prefix+ "delirole <role>`", value="Delete an invite role reward", inline=False)
    embed.add_field(name="`"+prefix+ "iroles`", value="Display all invite role rewards", inline=False)
    embed.add_field(name="`"+prefix+ "fetch`", value="Fetch all previous invites", inline=False)
    embed.add_field(name="`"+prefix+ "invite`", value="Show all your valid invite links.", inline=False)
    embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
    embed.set_footer(text="________________________\n<> Required | [] Optional\nMade By Zennara#8377")
    await message.channel.send(embed=embed)

  minusMessageContent = messagecontent.replace("<","").replace(">","").replace("@","").replace("!","").replace("&","")
  
  if messagecontent.startswith(prefix + 'invites'):
    #get user (member object)
    isInGuild = False
    if (messagecontent == prefix + 'invites'):
      user = message.author
      isInGuild = True
    else:
      dbUser = None
      #get db user
      if str(minusMessageContent[-18:]) in db[str(message.guild.id)]:
        dbUser = db[str(message.guild.id)][str(minusMessageContent[-18:])]
      else:
        await error(message, "Invalid user or user has no invites.")
        return
      #get actual member
      if message.guild.get_member(int(minusMessageContent[-18:])) != None:
        user = message.guild.get_member(int(minusMessageContent[-18:]))
        isInGuild = True
    #get vars
    if isInGuild:
      #check if in guild
      if str(user.id) not in db[str(message.guild.id)]:
        db[str(message.guild.id)][str(user.id)] = ["",0,0,0]
      Name = user.name + "#" + str(user.discriminator)
      Pfp = user.avatar_url
      Invites = db[str(message.guild.id)][str(user.id)][2]
      Leaves = db[str(message.guild.id)][str(user.id)][3]
      inviterUser = db[str(message.guild.id)][str(user.id)][1]
      joinCode = db[str(message.guild.id)][str(user.id)][0]
    else:
      Name = "<@"+str(minusMessageContent[-18:])+">"
      Pfp = ""
      Invites = dbUser[2]
      Leaves = dbUser[3]
      inviterUser = dbUser[1]
      joinCode = dbUser[0]
    totalInvites = Invites - Leaves
    #check for invite code and inviter
    if joinCode != "":
      getMember = message.guild.get_member(int(inviterUser))
      if getMember != None:
        text = "**"+getMember.name + "#" + str(getMember.discriminator)+"**"
      else:
        text = "<@"+str(inviterUser)+">"
      addition = "\nInvited by: " + text + " with code **"+joinCode+"**"
    else:
      addition = ""
    embed = discord.Embed(color=0x00FF00, description="User has **" + str(totalInvites) + "** invites! (**" + str(Invites) + "** regular, **-" + str(Leaves) + "** leaves)"+addition)
    if isInGuild:
      embed.set_author(name="@" + Name, icon_url=Pfp)
    else:
      embed = discord.Embed(color=0x00FF00, description=Name+"\nUser has **" + str(totalInvites) + "** invites! (**" + str(Invites) + "** regular, **-" + str(Leaves) + "** leaves)"+addition)
    if rand:
      embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
    await message.channel.send(embed=embed)

  #edit amounts
  if messagecontent.startswith(prefix + "edit"):
    if checkPerms(message):
      #split content
      splits = minusMessageContent.split()
      #check argument amounts
      if len(splits) >= 3 and len(splits) <= 4:
        #get leaves/Invites
        if splits[1] == "invites" or splits[1] == "leaves":
          #check if 2nd arg is a number
          if splits[2].isnumeric():
            #check for limits
            if int(splits[2]) >= 0 and int(splits[2]) < 1000000000:
              if len(splits) == 4:
                #check if user id at end of message is in db
                if str(minusMessageContent[-18:]) not in db[str(message.guild.id)]:
                  #check numeric
                  if minusMessageContent[-18:].isnumeric():
                    #check if proper member
                    if message.guild.get_member(int(minusMessageContent[-18:])):
                      #write to db
                      db[str(message.guild.id)][str(minusMessageContent[-18:])] = ["",0,0,0]
                    else:
                      await error(message, "User does not exist in the server cache.")
                      return
                  else:
                    await error(message, "User does not exist in the server cache.")
                    return
                user = str(minusMessageContent[-18:])
              else:
                user = str(message.author.id)
              #get change amount
              if splits[1] == "invites":
                change = 2
              else:
                change = 3
              #set change amount
              db[str(message.guild.id)][user][change] = int(splits[2])
              #send confirmation message
              embed = discord.Embed(color=0x00FF00, description="User now has **"+splits[2]+"** "+splits[1]+".")
              if rand:
                embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
              await message.channel.send(embed=embed)
              await checkRewards(message.guild.get_member(int(user)))
            else:
              await error(message, "Number out of range. This should be between `0` and `1,000,000,000`.")
          else:
            await error(message, "Invalid amount. This should be a number.")
        else:
          await error(message, "Invalid edit type. The first argument should be `invites` or `leaves`.")
      else:
        await error(message, "Invalid argument amount. Must be between `2` and `3`.")

  #change prefix
  if messagecontent.startswith(prefix + "prefix"):
    if checkPerms(message):
      if not any(x in messagecontent for x in ["!","`","<",">","@","&"]):
        if len(messagecontent) <= len(prefix) + 10:
          db[str(message.guild.id)]["prefix"] = message.content.lower().split()[1:][0]
          embed = discord.Embed(color=0x00FF00, description ="Prefix is now `" + message.content.split()[1:][0] + "`")
          embed.set_author(name="Prefix Change")
          if rand:
            embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await message.channel.send(embed=embed)
        else:
          await error(message, "Prefix must be between `1` and `3` characters.")
      else:
        await error(message, "Prefix can not contain `` ` `` , `_` , `~` , `*` , `<` , `>` , `@` , `&` , `!`")

  #invite leaderboard
  if messagecontent.startswith(prefix + "leaderboard"):
    embed = discord.Embed(color=0xFFFFFF, description="*This may take a few seconds.*")
    embed.set_author(name="⌛ | Leaderboard Loading...", icon_url=message.guild.icon_url)
    embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
    message2 = await message.channel.send(embed=embed)
    tmp = {}
    tmp = dict(db[str(message.guild.id)])
    #make new dictionary to sort
    tempdata = {}
    for key in tmp.keys():
      #all other dataEntries
      if key != "iroles" and key != "prefix":
        #check if it has any invitees or leaves
        if tmp[key][3] != 0 or tmp[key][2] != 0:
          tempdata[key] = tmp[key][2] - tmp[key][3]
    #sort data
    order = sorted(tempdata.items(), key=lambda x: x[1], reverse=True)
    #get page number
    page = 1
    page = int(page)
    cnt = messagecontent.split()
    #check length
    if len(cnt) > 1:
      if str(cnt[1]).isnumeric():
        page = int(messagecontent.split()[1])
      else:
        embed = discord.Embed(color=0xFF0000, description="Invalid Page. Currently, this should be between `1` and `"+str(math.ceil(len(order) / 10))+"`.")
        await message2.edit(embed=embed)
        return
    if int(page) >= 1 and int(page) <= math.ceil(len(order) / 10):
      #store all the users in inputText to later print
      inputText = ""
      count = 1
      for i in order:
        if count <= page * 10 and count >= page * 10 - 9:
          inputText += "\n`[" + str(count) +"]` <@!" + str(i[0]) + "> | **" + str(i[1]) + "** invites (**" + str(tmp[str(i[0])][2]) + "** regular, **-" + str(tmp[str(i[0])][3]) + "** leaves)"
        count += 1
      #print embed
      embed = discord.Embed(color=0x00FF00, description=inputText)
      embed.set_author(name=message.guild.name+" Invite Leaderboard", icon_url=message.guild.icon_url)
      if rand:
        embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
      embed.set_footer(text="Page " + str(page) + "/" + str(math.ceil(len(order) / 10)))
      await message2.edit(embed=embed)
    else:
      embed = discord.Embed(color=0xFF0000, description="Invalid Page. Currently, this should be between `1` and `"+str(math.ceil(len(order) / 10))+"`.")
      await message2.edit(embed=embed)

  #fetch previous guild invites
  if messagecontent == prefix+"fetch":
    if checkPerms(message):
      #local message
      reactionMessage = None
      #for await fucntion
      async def reactionClearAsync(reaction, user):
        await reaction.remove(user)
      def check(reaction, user):
        #check message and author
        if reactionMessage == reaction.message and user == message.author:
          #check reaction
          if str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌':
            asyncio.create_task(reactionClearAsync(reaction, user))
            return True
      embed = discord.Embed(color=0x593695, description="**WARNING: Doing so may result in data loss. Continue?**\nReact with ✅ to confirm, or ❌ to cancel.")
      embed.set_author(name="❔ | @" + client.user.name, icon_url=client.user.avatar_url)
      message2 = await message.channel.send(embed=embed)
      reactionMessage = message2
      await message2.add_reaction('✅')
      await message2.add_reaction('⚫')
      await message2.add_reaction('❌')
      try:
        #wait for reaction
        reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=check)
      except asyncio.TimeoutError:
        #timeout message
        embed = discord.Embed(color=0xFF0000, description="Message timed out. Interactive messages time out after `15` seconds.")
        await message2.edit(embed=embed)
      else:
        #check for confirm or cancel
        if reaction.emoji == '✅':
          embed = discord.Embed(color=0xFFFFFF, description="⌛ | **Loading Previous Invites**")
          embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await message2.edit(embed=embed)
          #reset inviters invites
          for invite in await message.guild.invites():
            #check if inviter in db
            if str(invite.inviter.id) in db[str(message.guild.id)]:
              #reset invites
              db[str(message.guild.id)][str(invite.inviter.id)][2] = 0
              db[str(message.guild.id)][str(invite.inviter.id)][3] = 0
          #loop through invites in guild
          for invite in await message.guild.invites():
            #check if inviter in db
            if str(invite.inviter.id) not in db[str(message.guild.id)]:
              db[str(message.guild.id)][str(invite.inviter.id)] = ["",0,0,0]
            #add to invites
            db[str(message.guild.id)][str(invite.inviter.id)][2] += int(invite.uses)
          embed = discord.Embed(color=0x00FF00, description="**Previous Invites Fetched**")
          if rand:
            embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await message2.edit(embed=embed)
        else:
          embed = discord.Embed(color=0x00FF00, description="Fetch invites cancelled.")
          await message2.edit(embed=embed)
      await message2.clear_reactions()

  #add irole
  if messagecontent.startswith(prefix + "addirole"):
    if checkPerms(message):
      newContent = minusMessageContent.split()
      #check if enough args
      if len(newContent) == 3:
        #check if second arg is number
        if newContent[1].isnumeric():
          #check if number is too big
          if int(newContent[1]) >= 0 and int(newContent[1]) < 1000000000:
            #check if roleID is a number
            if newContent[2].isnumeric():
              #check if its a valid role in the guild
              if message.guild.get_role(int(newContent[2])):
                #check if role exists in db already
                if newContent[2] not in db[str(message.guild.id)]["iroles"]:
                  role = message.guild.get_role(int(newContent[2]))
                  #check role heirarchy
                  if message.guild.get_member(int(client.user.id)).top_role > role:
                    db[str(message.guild.id)]["iroles"][str(role.id)] = int(newContent[1])
                    embed = discord.Embed(color=0x00FF00, description="Users will now recieve the role "+role.mention+" if they invite **"+newContent[1]+"** member" + ("" if newContent[1] == "1" else "s") + ".")
                    if rand:
                      embed.add_field(name="᲼",value="\n\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                    await message.channel.send(embed=embed)
                    for c in await message.guild.invites():
                      await checkRewards(message.guild.get_member(c.inviter.id))
                  else:
                    await error(message, "The role " +role.mention+ " is too high in the server hierarchy.\nMy top role is " +message.guild.get_member(int(client.user.id)).top_role.mention+ ".")
                else:
                  await error(message, "Role already has a reward assigned to it.")
              else:
                await error(message, "Invalid role. Check your ID or mention.")
            else:
              await error(message, "The argument, `<role>` needs to be the role mention or ID.")
          else:
            await error(message, "Number out of range. This should be between `0` and `1,000,000,000`.")
        else:
          await error(message, "Invalid amount. This should be a number.")
      else:
        await error(message, "Invalid argument amount. This must be `<invites> <role>`.")

  #delete irole
  if messagecontent.startswith(prefix + "delirole"):
    if checkPerms(message):
      newContent = minusMessageContent.split()
      #check if enough args
      if len(newContent) == 2:
        #check if second arg is number
        if newContent[1].isnumeric():
          #check if its a valid role in the guild
          if message.guild.get_role(int(newContent[1])):
            #check if role exists in db already
            if newContent[1] in db[str(message.guild.id)]["iroles"]:
              role = message.guild.get_role(int(newContent[1]))
              del db[str(message.guild.id)]["iroles"][str(role.id)]
              embed = discord.Embed(color=0x00FF00, description="The role reward for " +role.mention+ " has been **deleted**.")
              if rand:
                embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
              await message.channel.send(embed=embed)
            else:
              await error(message, "No current reward for specified role.")
          else:
            await error(message, "Invalid role. Check your ID or mention.")
        else:
          await error(message, "The argument, `<role>` needs to be the role mention or ID.")
      else:
        await error(message, "Invalid argument amount. This must be `<role>`.")

  #show all invite role-rewards
  if messagecontent == prefix + "iroles":
    count = 0
    #get all RR messages
    embed = discord.Embed(color=0x00FF00, description="**Invite Role-Rewards**")
    embed.set_author(name=message.guild.name, icon_url=message.guild.icon_url)
    for irole in db[str(message.guild.id)]["iroles"]:
      if count == 25:
        count = 0
        await message.channel.send(embed=embed)
        embed = discord.Embed(color=0x00FF00, description="")
      embed.add_field(name="Invites: "+str(db[str(message.guild.id)]["iroles"][irole]), value="**Role:** <@&" + irole + ">")
      count += 1
    await message.channel.send(embed=embed)

  #return invite
  if messagecontent == prefix + "invite":
    if await message.guild.invites():
      inviteText = "**Code** \_\_\_\_\_\_\_\_\_\_\_\_ **Uses** \_\_ **Expires in**\n"
      for invite in await message.guild.invites():
        if invite.inviter.id == message.author.id:
          dTime = str(datetime.timedelta(seconds=invite.max_age))
          if dTime != "0:00:00":
            if "day" in dTime:
              newTime = (dTime[0:6] if dTime.endswith("0:00:00") else dTime[8:]).replace(",","")
            else:
              newTime = dTime
          else:
            newTime = "Never"
          inviteText = inviteText + "`" +invite.code+""+(" "*(15-len(invite.code)))+""+ " | " +str(invite.uses)+ " / " +(str(invite.max_uses) if invite.max_uses != 0 else "∞")+ " | " + newTime+ (" "*(15-len(newTime)))+"`"+invite.channel.mention +"\n"
      embed = discord.Embed(color=0x00FF00, description=inviteText)
      embed.set_author(name=message.author.name+"#"+str(message.author.discriminator)+"'s Invites", icon_url=message.author.avatar_url)
      if rand:
        embed.add_field(name="᲼",value="\n\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
      await message.channel.send(embed=embed)
        


@client.event
async def on_guild_join(guild):
  db[str(guild.id)] = {"prefix": "i/"}
  db[str(guild.id)]["iroles"] = {}



#client.loop.create_task(getInvites())

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))