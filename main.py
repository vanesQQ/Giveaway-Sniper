import os
import re
import asyncio
import json
import discord
from datetime import datetime
from discord.ext import commands
from colorama import Fore
from discord import Webhook, RequestsWebhookAdapter
import requests


bot = commands.Bot(command_prefix=".", help_command=None, self_bot=True)


with open("config.json") as f:
    data = json.load(f)


headers = {'Authorization': data["discord_token"]}


messageID = None


def timenow():
    return datetime.now().strftime('%H:%M:%S')

def menu():
    os.system("cls")
    print(Fore.LIGHTMAGENTA_EX + f"""
       ___________    ___________ _       _______  __
      / ____/  _/ |  / / ____/   | |     / /   \ \/ /
     / / __ / / | | / / __/ / /| | | /| / / /| |\  / 
    / /_/ // /  | |/ / /___/ ___ | |/ |/ / ___ |/ /  
    \____/___/  |___/_____/_/__|_|__/|__/_/  |_/_/   
      / ___// | / /  _/ __ \/ ____/ __ \             
      \__ \/  |/ // // /_/ / __/ / /_/ /             
     ___/ / /|  // // ____/ /___/ _, _/              
    /____/_/ |_/___/_/   /_____/_/ |_|               
                                                 

[+] User: {bot.user}                                            
[+] User ID: {bot.user.id}      

    """)

@bot.event
async def on_ready():
    menu()


@bot.event
async def on_message(message):

    gotMatch = False
    channel = message.channel
    if type(channel) == discord.TextChannel:
        async for message in channel.history(limit=1):
            global messageID
            if message.author.id in data["giveaway_bot_id"]:
                for i in data["giveaway_trigger"]:
                    x = re.search(i, message.embeds[0].description) # trigger
                    if x:
                        gotMatch = True
                        break

        if gotMatch:
            if messageID != message.id:
                messageID = message.id
                print('\n\n')
                print(f'[{timenow()}][Giveaway] Bot: {message.author}')
                print(f'[{timenow()}][Giveaway] Server: {message.guild}')
                print(f'[{timenow()}][Giveaway] Channel: {message.channel}')

                r = requests.post(f"https://discord.com/api/v9/channels/{message.channel.id}/invites", headers=headers, json={"validate":None,"max_age":604800,"max_uses":0,"target_type":None,"temporary":False})
                print(f'[{timenow()}][Giveaway] Invite: {r.json()["code"]}')
                
                webhook = Webhook.from_url(data["giveaway_webhook"], adapter=RequestsWebhookAdapter())
                embed = message.embeds[0]
                embed.set_author(name=message.embeds[0].author.name, icon_url=message.author.avatar_url)
                embed.set_thumbnail(url=message.guild.icon_url)
                embed.add_field(name="Jump", value=f"[Go to message!]({message.jump_url})", inline=False)
                embed.add_field(name="Join", value=f"[Join giveaway!](https://discord.gg/{r.json()['code']})", inline=False)
                webhook.send(embed=embed, content="@everyone")
                
                await asyncio.sleep(data["reaction_cooldown"])
                print("p")
                try:
                    await message.add_reaction("🎉") # reaction emoji
                    print(f'[{timenow()}][Giveaway] Giveaway Entered')
                except:
                    pass

    await bot.process_commands(message)


bot.run(data["discord_token"], bot=False)