# ManageInvites
A Discord bot capable of tracking invites and awarding roles if members invite a certain amount of people. This bot was created in version 1.7.3 of the [discord.py](https://discordpy.readthedocs.io/en/stable/api.html) api. However, discord.py is [no longer being developed](https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1). This project will be continued, and most likely moved to a well maintained fork, like [nextcord](https://github.com/nextcord/nextcord).

## Enjoy Free Hosting?
If you enjoy using my bot in your server, please consider [donating](https://www.paypal.me/keaganlandfried). Even the smallest amount ensures I can keep these bots free and online.

## Command List
| **Command** | **Arguments**                           | **Description**                         | **Public?** |
|-------------|-----------------------------------------|-----------------------------------------|-------------|
| invites     | [member]                                | Show your total invites                 | yes         |
| leaderboard | [page]                                  | Display a server invite leaderboard     | yes         |
| edit        | \<invites\|leaves\> \<amount\> [member] | Edit a members invites or leaves        | no          |
| addirole    | \<invites\> \<role\>                    | Add a new invite role reward            | no          |
| delirole    | \<role\>                                  | Delete a invite role reward             | no          |
| iroles      | none                                    | Display all invite role rewards         | yes         |
| fetch       | none                                    | Grab all previous invites (use on join) | no          |
| invite      | none                                    | Display all your invite links           | yes         |
