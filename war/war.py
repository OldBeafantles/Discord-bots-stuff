import discord
from discord.ext import commands
import random
from random import randint
from random import choice as randchoice
from .utils import checks
from .utils.dataIO import dataIO
from datetime import datetime
import time
import aiohttp
import asyncio
import os
from __main__ import send_cmd_help
from __main__ import settings
import math
import threading
from random import shuffle
from __main__ import settings as bot_settings
import glob
import re
import logging
import json
import datetime



class War:

    def __init__(self, bot):
        self.bot=bot
        self.persos = dataIO.load_json("data/war/Persos.json")
        self.masterid = dataIO.load_json("data/red/settings.json")["OWNER"]
        # Persos List
        self.list_persos = self.persos['list_persos']
        self.tournament = dataIO.load_json("data/war/tournament.json")
        self.waiting = dataIO.load_json("data/war/waiting.json")
        self.teams = dataIO.load_json("data/war/teams.json")
        self.bosses = dataIO.load_json("data/war/bosses.json")
        self.Nregister = 16 #The number of people for a tournament
        # Tournament Details
        self.schedule = "19/08/2016 12:00"
        self.tourduration = "19/08/2016 12:00-13:30 PST(Global Time)"
        self.fightserver = "217727307954126849"
        self.fightchannel = "217727307954126849"
        self.invitelink = "https://discord.gg/bgmFc2Z" #The link to join the server of the tournament
        self.judgeid = "110315307712655360" # [7DS] 天元突破グレンラガン FOUND STH!!!!

    ##Get username from userid
    def getMember(self, userid):
        for server in self.bot.servers:
            for member in server.members:
                if member.id == userid:
                    return member
    
    ##Get server from serverid
    def getServer(self, serverid):
        for server in self.bot.servers:
            if server.id == serverid:
                return server


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def create_team(self, ctx, user : discord.Member):
        """Create a new team and make the user the leader of this one"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if user.id not in self.teams:
            found = False
            for team in self.teams:
                if user.id in team:
                    found = True
                    break
            if not found:
                persos = "<@" + user.id + ">, please choose your character between the following ones:"
                for x in range(0, len(self.list_persos)):
                    persos += str(x+1) + ") " + self.list_persos[x] + "\n"
                message0 = await self.bot.say(persos)
                answer = await self.bot.wait_for_message(timeout=60,author=user,channel=ctx.message.channel)
                if answer == None:
                    await self.bot.say("I don't want to wait anymore, I cancel the creation! :grimacing:")
                    await self.bot.delete_message(message0)
                else:
                    try:
                        choix1 = int(answer.content)
                    except ValueError:
                        await self.bot.say("That's not a **number**, I cancel the creation! :grimacing:")
                        await self.bot.delete_message(message0)
                    if choix1<1 or choix1>len(self.list_persos):
                        await self.bot.say("That's not a **correct number**, I cancel the creation! :grimacing:")
                        await self.bot.delete_message(message0)
                    elif choix1>0 and choix1<len(self.list_persos)+1:
                        await self.bot.say("Here's your character : **"+ self.list_persos[choix1-1] + "** \n" + self.persos[self.list_persos[choix1-1] + " presentation"] + "\n")
                        self.teams[user.id] = {'leader' : user.id, 'members' : []}
                        dataIO.save_json("data/war/teams.json", self.teams)
                        await self.bot.say("Done!")
            else:
                await self.bot.say("This member is already in a team! :grimacing:")
        else:
            await self.bot.say("This member is already the leader of a team! :grimacing:")


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def del_team(self, ctx, user : discord.Member):
        """Delete a team, using the leader of this one"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if user.id in self.teams:
            del self.teams[user.id]
            dataIO.save_json("data/war/teams.json", self.teams)
            await self.bot.say("Done!")
        else:
            await self.bot.say("This member wasn't even the leader of a team! :wink:")


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def show_team(self, ctx, user : discord.Member = None):
        """Shows all the leaders of the teams"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if user == None:
            if len(self.teams) != 0:
                msg = "```Markdown\nList of all the teams\n=====================\n\n"
                x = 1
                for team in self.teams:
                    leader = self.getMember(team)
                    msg += "[" + str(x) + "][" + leader.name  + "#" + leader.discriminator + "]\n"
                    x += 1
                msg += "```"
                await self.bot.say(msg)
            else:
                await self.bot.say("There's no team! :grimacing:")
        else:
            if user.id in self.teams:
                leader = self.getMember(user.id)
                msg = "```Markdown\n" + leader.name + "#" + leader.discriminator + "'s team:\n===========================\n\n"
                for member in self.teams[user.id]['members']:
                    Tmember = self.getMember(member)
                    if Tmember:
                        msg += Tmember.name + "#" + Tmember.discriminator + "\n"
                    else:
                        msg += "Doesn't exist anymore!\n"
                msg += "```"
                await self.bot.say(msg)
            else:
                found = False
                for team in self.teams:
                    if user.id in team['members']:
                        leader = self.getMember(team['leader'])
                        msg = "```Markdown\n" + leader.name + "#" + leader.discriminator + "'s team:\n===========================\n\n"
                        for member in self.teams[user.id]['members']:
                            Tmember = self.getMember(member)
                            if Tmember:
                                msg += Tmember.name + "#" + Tmember.discriminator + "\n"
                            else:
                                msg += "Doesn't exist anymore!\n"
                        msg += "```"
                        await self.bot.say(msg)
                        found = True
                        break
                if not found:
                    await self.bot.say("This user doesn't belong to any team! :grimacing:")

    @commands.command(pass_context=True)
    async def my_team(self, ctx):
        """Shows you team"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if ctx.message.author.id in self.teams:
            msg = "```Markdown\n" + ctx.message.author.name + "#" + ctx.message.author.discriminator + "'s team:\n===========================\n\n"
            for member in self.teams[ctx.message.author.id]['members']:
                Tmember = self.getMember(member)
                if Tmember:
                    msg += Tmember.name + "#" + Tmember.discriminator + "\n"
                else:
                    msg += "Doesn't exist anymore!\n"
            msg += "```"
            await self.bot.say(msg)
        else:
            found = False
            for team in self.teams:
                if user.id in team['members']:
                    leader = self.getMember(team['leader'])
                    msg = "```Markdown\n" + leader.name + "#" + leader.discriminator + "'s team:\n===========================\n\n"
                    for member in self.teams[user.id]['members']:
                        Tmember = self.getMember(member)
                        if Tmember:
                            msg += Tmember.name + "#" + Tmember.discriminator + "\n"
                        else:
                            msg += "Doesn't exist anymore!\n"
                    msg += "```"
                    await self.bot.say(msg)
                    found = True
                    break
            if not found:
                await self.bot.say("You don't belong to any team! :grimacing:")


    @commands.command(pass_context=True)
    async def invite_team(self, ctx, user : discord.Member):
        """Invites a member to your team"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if ctx.message.author.id in self.teams:

            if user.id not in self.teams[ctx.message.author.id]['members'] and user.id != self.teams[ctx.message.author.id]['leader']:

                found = False
                for team in self.teams:
                    if user.id in self.teams[team]['members'] or user.id == self.teams[team]['leader']:
                        found = True
                        break

                if not found:
                    persos = "<@" + user.id + ">, IF YOU WANT TO JOIN " + ctx.message.author.name + "#" + ctx.message.author.discriminator + "'s TEAM, please choose your character between the following ones. Otherwise, just type `cancel`:\n\n"
                    for x in range(0, len(self.list_persos)):
                        persos += str(x+1) + ") " + self.list_persos[x] + "\n"
                    message0 = await self.bot.say(persos)
                    answer = await self.bot.wait_for_message(timeout=60,author=user,channel=ctx.message.channel)
                    if answer == None:
                        await self.bot.say("I don't want to wait anymore, I cancel the invitation! :grimacing:")
                        await self.bot.delete_message(message0)
                    else:
                        try:
                            choix1 = int(answer.content)
                        except ValueError:
                            if choix1.content != "cancel":
                                await self.bot.say("That's not a **number**, I cancel the invitation! :grimacing:")
                            else:
                                await self.bot.say("Invitation cancelled! :grimacing:")
                            await self.bot.delete_message(message0)
                        if choix1<1 or choix1>len(self.list_persos):
                            await self.bot.say("That's not a **correct number**, I cancel the invitation! :grimacing:")
                            await self.bot.delete_message(message0)
                        elif choix1>0 and choix1<len(self.list_persos)+1:
                            await self.bot.say("Here's your character : **"+ self.list_persos[choix1-1] + "** \n" + self.persos[self.list_persos[choix1-1] + " presentation"] + "\n")
                            self.teams[ctx.message.author.id]['members'].append(user.id)
                            dataIO.save_json("data/war/teams.json", self.teams)
                            await self.bot.say("Done!\n" + user.name + "#" + user.discriminator + " now belongs to " + ctx.message.author.name + "#" + ctx.message.author.discriminator + "'s team!")
                else:
                    await self.bot.say(user.name + "#" + user.discriminator + " already belongs to another team! :grimacing:")
            else:
                await self.bot.say(user.name + "#" + user.discriminator + " is already in your team! :wink:")
        else:
            await self.bot.say("You're not even the leader of any team! :grimacing:")


    @commands.command(pass_context=True)
    async def rem_team_member(self, ctx, user : discord.Member):
        """Removes a membre from your team"""

        self.teams = dataIO.load_json("data/war/teams.json")

        if ctx.message.author.id in self.teams:

            if user.id in self.teams[ctx.message.author.id]['members']:

                self.teams[ctx.message.author.id]['members'].remove(user.id)
                dataIO.save_json("data/war/teams.json", self.teams)
                await self.bot.say("Done!")

            else:
                await self.bot.say(user.name + "#" + user.discriminator + " wasn't even belonging to your team! :wink:")

        else:
            await self.bot.say("You're not even the leader of any team! :grimacing:")


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def add_boss(self, ctx, *text):
        """Add a boss (Boss name#Boss picture's link#Boss HP#Boss attack 1 name#Boss attack 1 damage#...#Boss attack 6 name#Boss attack 6 damage)"""
        text = " ".join(text)
        infos = text.split("#")
        if len(infos) != 15:
            await self.bot.say("The format isn't correct! :grimacing:")
        else:
            self.bosses = dataIO.load_json("data/war/bosses.json")
            if infos[0] not in self.bosses:
                try:
                    infos[2] = int(infos[2])
                    infos[3] = int(infos[3])
                    infos[5] = int(infos[5])
                    infos[7] = int(infos[7])
                    infos[9] = int(infos[9])
                    infos[11] = int(infos[11])
                    infos[13] = int(infos[13])
                    self.bosses[infos[0]] = {}
                    self.bosses[infos[0]]["presentation"] = infos[1]
                    self.bosses[infos[0]]["HP"] = infos[2]
                    for i in range(1,7):
                        self.bosses[infos[0]]["sort " + str(i) + " nom"] = infos[i * 2 + 1]
                        self.bosses[infos[0]]["sort " + str(i) + " degats"] = infos[2 + i * 2]
                    dataIO.save_json("data/war/bosses.json", self.bosses)
                    await self.bot.say("The boss has been successfully added!")
                except ValueError:
                    await self.bot.say("The format of the damages isn't correct.")
            else:
                await self.bot.say("There's already a boss with this name, I can't do that! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def del_boss(self, ctx, *text):
        """Delete a boss using his name"""
        text = " ".join(text)
        self.bosses = dataIO.load_json("data/war/bosses.json")
        if text in self.bosses:
            del self.bosses[text]
            dataIO.save_json("data/war/bosses.json", self.bosses)
            await self.bot.say("Done!")
        else:
            await self.bot.say("This character doesn't even exist! :grimacing:")


    @commands.command(pass_context=True)
    async def list_bosses(self,ctx):
        """Lists all the bosses"""

        self.bosses = dataIO.load_json("data/war/bosses.json")

        if len(self.bosses) != 0:
            msg = "```Markdown\nList of bosses\n======================\n\n"
            x = 1
            for boss in self.bosses:
                msg += "[" + str(x) + "][" + boss + "]\n"
                x += 1
            msg += "```"
            await self.bot.say(msg)

        else:
            await self.bot.say("No bosses! :grimacing:")

    @commands.command(pass_context=True)
    async def boss_stats(self, ctx, *boss):
        """Shows the boss stats"""
        self.bosses = dataIO.load_json("data/war/bosses.json")
        boss = " ".join(boss).title()
        if boss in self.bosses:
            await self.bot.say("Here's the boss stats: **" + boss + "**\n" + self.bosses[boss]["presentation"])
        elif boss.isdigit():
            choix = int(boss)
            if choix <= len(self.bosses) and choix > 0:
                await self.bot.say("Here's the character stats: **"+ self.bosses[choix-1] + "** \n" + self.bosses[choix - 1]["presentation"])
            else:
                await self.bot.say("This number isn't correct! :grimacing:")
        else:
            await self.bot.say("There's no such boss listed in the War Bot. Please type `[p]list_bosses` for all bosses")


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def del_char(self,ctx,*text):
        """Delete a character using his name"""
        text = " ".join(text)
        self.persos = dataIO.load_json("data/war/Persos.json")
        self.list_persos = self.persos['list_persos']
        if text in self.list_persos:
            self.list_persos.remove(text)
            del self.persos[text + " presentation"]
            for i in range(1,7):
                del self.persos[text + " sort " + str(i) + " nom"]
                del self.persos[text + " sort " + str(i) + " degats"]
            dataIO.save_json("data/war/Persos.json", self.persos)
            await self.bot.say("The character has been successfully deleted!")
        else:
            await self.bot.say("This character doesn't even exist! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def add_char(self,ctx,*text):
        """Add a character for the bot (Character name#Character picture's link#Character attack 1 name#Character attack 1 damage#...#Character attack 6 name#Character attack 6 damage)"""
        text = " ".join(text)
        infos = text.split("#")
        if len(infos) != 14:
            await self.bot.say("The format isn't correct! :grimacing:")
        else:
            self.persos = dataIO.load_json("data/war/Persos.json")
            self.list_persos = self.persos['list_persos']
            if infos[0] not in self.list_persos:
                try:
                    infos[3] = int(infos[3])
                    infos[5] = int(infos[5])
                    infos[7] = int(infos[7])
                    infos[9] = int(infos[9])
                    infos[11] = int(infos[11])
                    infos[13] = int(infos[13])
                    if infos[3] + infos[5] + infos[7] + infos[9] + infos[11] + infos[13] != 100:
                        await self.bot.say("The total of the damages isn't equal to 100, I just wanted to notice that!")
                    self.persos = dataIO.load_json("data/war/Persos.json")
                    self.list_persos = self.persos['list_persos']
                    self.persos['list_persos'].append(infos[0])
                    self.persos[infos[0] + " presentation"] = infos[1]
                    for i in range(1,7):
                        self.persos[infos[0] + " sort " + str(i) + " nom"] = infos[i * 2]
                        self.persos[infos[0] + " sort " + str(i) + " degats"] = infos[1 + i * 2]
                    dataIO.save_json("data/war/Persos.json", self.persos)
                    await self.bot.say("The character has been successfully added!")
                except ValueError:
                    await self.bot.say("The format of the damages isn't correct.")
            else:
                await self.bot.say("There's already a character with this name, I can't do that! :grimacing:")

    @commands.command(pass_context=True)
    async def fight(self,ctx,user : discord.Member = True):
        """ Start a fight with someone (2 players)"""
        self.persos = dataIO.load_json("data/war/Persos.json")
        self.list_persos = self.persos['list_persos']
        await self.bot.say("<@" + user.id + ">, which character between the following ones do you want to pick? (Just type the corresponding number)")
        persos = "1) " + self.list_persos[0] + "\n"
        for x in range(1, len(self.list_persos)):
            persos += str(x+1) + ") " + self.list_persos[x] + "\n"
        message0 = await self.bot.say(persos)
        answer = await self.bot.wait_for_message(timeout=60,author=user,channel=ctx.message.channel)
        if answer == None:
            await self.bot.say("I don't want to wait anymore, I cancel the fight! :grimacing:")
            await self.bot.delete_message(message0)
        else:
            try:
                choix1 = int(answer.content)
            except ValueError:
                await self.bot.say("That's not a **number**, I cancel the fight! :grimacing:")
                await self.bot.delete_message(message0)
            if choix1<1 or choix1>len(self.list_persos):
                await self.bot.say("That's not a **correct number**, I cancel the fight! :grimacing:")
                await self.bot.delete_message(message0)
            elif choix1>0 and choix1<len(self.list_persos)+1:
                await self.bot.say("Here's your character : **"+ self.list_persos[choix1-1] + "** \n" + self.persos[self.list_persos[choix1-1] + " presentation"] + "\n")                               
                await self.bot.say("And you <@" + ctx.message.author.id + ">, which character do you want to pick?")
                answer = await self.bot.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
                if answer==None:
                    await self.bot.say("I don't want to wait anymore, I cancel the fight! :grimacing:")
                    await self.bot.delete_message(message0)
                else:
                    try:
                        choix2 = int(answer.content)
                    except ValueError:
                        await self.bot.say("That's not a **number**, I cancel the fight! :grimacing:")
                        await self.bot.delete_message(message0)
                    if choix2<1 or choix2>len(self.list_persos):
                        await self.bot.say("That's not a **correct number**, I cancel the fight! :grimacing:")
                        await self.bot.delete_message(message0)
                    elif choix2>0 and choix2<len(self.list_persos)+1:
                        await self.bot.say("Here's your character : **"+ self.list_persos[choix2-1] + "** \n" + self.persos[self.list_persos[choix2-1] + " presentation"] + "\n")                 
                        await self.bot.delete_message(message0)
                        message = await self.bot.send_message(ctx.message.channel,"It's time to D-D-D-D-DUEL!")
                        data = ""
                        HP1=100
                        HP2=100
                        check=False
                        while check == False:
                            dé1 = str(randint(1, 6))
                            dé2 = str(randint(1, 6))
                            data=""
                            data+="         BEGINNING OF THE FIGHT            \n"
                            data+="-------------------------------------------\n"
                            data+="                                           \n"
                            data+="                                           \n"
                            data+="     Choice of the first one to play       \n"
                            data+="                                           \n"
                            data+="**" +  ctx.message.author.name +"** rolls the dice and gets a "  + dé1 + "!"
                            message = await self.bot.edit_message(message,data)
                            await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=2)
                            data=""
                            data+="         BEGINNING OF THE FIGHT            \n"
                            data+="-------------------------------------------\n"
                            data+="                                           \n"
                            data+="                                           \n"
                            data+="     Choice of the first one to play       \n"
                            data+="                                           \n"
                            data+="**" +  user.name +"** rolls the dice and gets a "  + dé2 + "!"
                            message = await self.bot.edit_message(message,data)
                            await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=2)
                            if dé1!=dé2:
                                if int(dé1)>int(dé2):
                                    premier = ctx.message.author
                                    deuxieme = user
                                    choixpremier = choix2
                                    choixdeuxieme = choix1
                                else:
                                    premier = user
                                    deuxieme = ctx.message.author
                                    choixpremier = choix1
                                    choixdeuxieme = choix2
                                check=True
                                await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=2)
                        data=""
                        data+="         BEGINNING OF THE FIGHT            \n"
                        data+="-------------------------------------------\n"
                        data+="                                           \n"
                        data+="                                           \n"
                        data+="     Choice of the first one to play       \n"
                        data+="                                           \n"
                        data+="So, it's **" +  premier.name +"** who'll begin!"
                        message = await self.bot.edit_message(message,data)
                        await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=4)
                        while HP1!=0 and HP2!=0:
                            dé = str(randint(1, 6))
                            degats = self.persos[self.list_persos[choixpremier-1] + " sort " + dé +" degats"]
                            test = premier.name + " uses **" + self.persos[self.list_persos[choixpremier-1] + " sort " + dé +" nom"] + "** ! " + deuxieme.name + " loses " + str(degats) + " HP!\n"
                            data=""
                            data+="                  FIGHT!                   \n"
                            data+="-------------------------------------------\n"
                            data+= premier.name + " : " + str(HP1) + " HP     VS    " + deuxieme.name + " : " + str(HP2) + " HP\n"
                            data+="                                           \n"
                            data+= premier.name + " rolls the dice and get a " + dé +"!\n" 
                            data+=test
                            message = await self.bot.edit_message(message,data)
                            HP2-=degats
                            await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=3)
                            if HP2<=0:
                                HP2=0
                            else:
                                dé = str(randint(1, 6))
                                degats = self.persos[self.list_persos[choixdeuxieme-1] + " sort " + dé +" degats"]
                                test=deuxieme.name + " uses **" + self.persos[self.list_persos[choixdeuxieme-1] + " sort " + dé +" nom"] + "** ! " + premier.name + " loses " + str(degats) + " HP!\n"    
                                data=""
                                data+="                  FIGHT!                   \n"
                                data+="-------------------------------------------\n"
                                data+= premier.name + " : " + str(HP1) + " PV     VS    " + deuxieme.name + " : " + str(HP2) + " PV\n"
                                data+="                                           \n"
                                data+= deuxieme.name + " rolls the dice and get a " + dé +"!\n" 
                                data+=test
                                message = await self.bot.edit_message(message,data)
                                HP1-=degats
                                if HP1<0:
                                    HP1=0
                                await self.bot.wait_for_message(content = 'azeazeaezaerazerzasdfsc', timeout=3)
                        data=""
                        data+="                 RESULTS                   \n"
                        data+="-------------------------------------------\n"
                        data+= premier.name + " : " + str(HP1) + " HP     VS    " + deuxieme.name + " : " + str(HP2) + " HP\n"
                        data+="                                           \n"
                        data+="                                           \n"
                        if HP1==0:
                            data+="**" + deuxieme.name + "** wins!\n"
                            gagnant = deuxieme
                        else:
                            data+="**" +  premier.name +"** wins!\n"
                            gagnant = premier
                        if gagnant.avatar == None:
                            data+=gagnant.default_avatar_url()
                        else:
                            data+="https://discordapp.com/api/users/" + gagnant.id +"/avatars/" +gagnant.avatar+".jpg"
                        message = await self.bot.edit_message(message,data)
            
        
    @commands.command(pass_context=True)
    async def charstat(self,ctx, *character):
        """Shows the stat sheet of the character"""
        self.persos = dataIO.load_json("data/war/Persos.json")
        self.list_persos = self.persos['list_persos']
        character =  " ".join(character)
        character = character.title()
        if character in self.list_persos:
            await self.bot.say("Here's the character stats: **"+ character + "** \n" + self.persos[character + " presentation"])
        elif character.isdigit():
            choix2 = int(character)
            if choix2<len(self.list_persos)+1 and choix2 > 0:
                await self.bot.say("Here's the character stats: **"+ self.list_persos[choix2-1] + "** \n" + self.persos[self.list_persos[choix2-1] + " presentation"])    
            else:
                await self.bot.say("This number isn't correct :grimacing:")
        else:
            await self.bot.say("There's no such character listed in the War Bot. Please type `[p]listchar` for all characters")

    @commands.command(pass_context=True)
    async def listchar(self,ctx):
        """Get the list of the playable characters"""
        self.persos = dataIO.load_json("data/war/Persos.json")
        self.list_persos = self.persos['list_persos']
        await self.bot.say("**List of characters available in War Bot:** \n\n")
        persos = str(1) + ") " + self.list_persos[0] + "\n"
        for x in range(1, len(self.list_persos)):
            persos += str(x+1) + ") " + self.list_persos[x] + "\n"
        await self.bot.say(persos)          
        
    @commands.command(pass_context=True)
    async def register(self,ctx):
        """Register for Tournament (16 Max)"""
        if ctx.message.server.id == self.fightserver or ctx.message.channel.id == self.fightchannel:
            userid = ctx.message.author.id
            if userid  in self.tournament:
                await self.bot.say("You're already registered! :wink:")
            else:
                if len(self.tournament)<self.Nregister:
                    self.tournament.append(userid)
                    dataIO.save_json("data/war/tournament.json", self.tournament)
                    await self.bot.say("You're now registered! :wink:")
                else:
                    if userid not in self.waiting:
                        self.waiting.append(userid)
                        dataIO.save_json("data/war/waiting.json", self.waiting)
                        await self.bot.say("There are already enough participants! :cry:\n Don't worry, you have been added to the waiting list at position **"+str(self.waiting.index(userid)+1)+"**.\nWe will send you a PM to inform you if you made it to the registration list")
                    else:
                        await self.bot.say("You are already in the waiting list at position **"+str(self.waiting.index(userid)+1)+"**.\nWe will send you a PM to inform you if you made it to the registration list")
        else:
            await self.bot.say("Tournament is only available for **"+self.getServer(self.fightserver).name+"**, you can join this server here : "+self.invitelink+"")

    @commands.command(pass_context=True)
    async def deregister(self,ctx):
        """Deregister yourself from Tournament"""
        if ctx.message.server.id == self.fightserver or ctx.message.channel.id == self.fightchannel:
            userid = ctx.message.author.id
            if userid in self.tournament:
                self.tournament.remove(userid)
                dataIO.save_json("data/war/tournament.json", self.tournament)
                await self.bot.say("You're deregistered from the tournament! :wink:")
                if len(self.tournament)==(self.Nregister-1) and len(self.waiting)>=1:
                    # Upgrade someone from waiting list to registration
                    waitingid = self.waiting[0]
                    self.waiting.remove(waitingid)
                    self.tournament.append(waitingid)
                    dataIO.save_json("data/war/tournament.json", self.tournament)
                    dataIO.save_json("data/war/waiting.json", self.waiting)
                    await self.bot.send_message(self.getMember(waitingid), "Congratulations! You have made it out of the waiting list into the Registration List for the Tournament. Please be there on time! :smile:")
            elif userid in self.waiting:
                self.waiting.remove(userid)
                dataIO.save_json("data/war/waiting.json",self.waiting)
                await self.bot.say("You're deregistered from the waiting list! :wink:")
            else:
                await self.bot.say("You are not in the Registered List! :wink:")
        else:
            await self.bot.say("Tournament is only available for **"+self.getServer(self.fightserver).name+"**, you can join this server here : "+self.invitelink+"")
        
    @commands.command(pass_context=True)
    async def list_participants(self,ctx):
        """List Tournament participants"""
        if ctx.message.server.id == self.fightserver or ctx.message.channel.id == self.fightchannel:
            msg_str = "__Registered Tournament Participants__\n\n"
            cc = 1 # counter
            for userid in self.tournament:
                msg_str+= str(cc)+") "+self.getMember(userid).name+"\n"
                cc+=1
            if len(self.waiting)>0:
                msg_str += "\n__Tournament Waiting List__\n\n"
                cc=1
                for userid in self.waiting:
                    msg_str+= str(cc)+") "+self.getMember(userid).name+"\n"
                    cc+=1
            await self.bot.say(msg_str)
        else:
            await self.bot.say("Tournament is only available for **"+self.getServer(self.fightserver).name+"**, you can join this server here : "+self.invitelink+"")

    @commands.command(pass_context=True)
    async def countdown(self,ctx):
        """Tournament countdown"""
        if ctx.message.server.id == self.fightserver or ctx.message.channel.id == self.fightchannel:
            dt_current = datetime.datetime.today() - datetime.timedelta(hours=10) # France time to PST
            dt_event = datetime.datetime.strptime(self.schedule,'%d/%m/%Y %H:%M')#convert to datetime
            dt_diff = dt_event - dt_current
            days = dt_diff.days
            hours = dt_diff.seconds//3600
            minutes = dt_diff.seconds//60%60
            msg_str = "The **Tournament** will be held on __"+self.schedule+" PST__\n(Global OPTC Game Time).\n\n"
            msg_str += "Countdown: **"+str(days)+"** Days **"+str(hours)+"** Hours **"+str(minutes)+"** Mins"
            await self.bot.say(msg_str)
        else:
            await self.bot.say("Tournament is only available for **"+self.getServer(self.fightserver).name+"**, you can join this server here : "+self.invitelink+"")

    @commands.command(pass_context=True)
    async def announcement(self,ctx):
        if ctx.message.server.id == self.fightserver or ctx.message.channel.id == self.fightchannel:
            """Tournament Announcement"""
            msg_str = "**__Tournament Announced__**\n"
            msg_str+= "Time: "+self.tourduration+"\n"
            msg_str+= "Venue: <#"+self.fightchannel+">\n"
            Mmember = self.getMember(self.judgeid).name
            if Mmember == None:
            	Mmember = "Unknown member"
            msg_str+= "Host: **" + Mmember + "**\n\n"
            msg_str+= "__Prizes:__\n"
            msg_str+= "1st Prize: 100 Million Beli\n"
            msg_str+= "2nd Prize: 50 Million Beli\n"
            msg_str+= "3rd Prize: 25 Million Beli\n"
            msg_str+= "All Paricipants will get __5 Million Belis__\n"
            msg_str+= "Limited to **" + self.Nregister + "** Participants! So HURRY UP!\n\n"
            msg_str+= "**%register**\tTo Register\n"
            msg_str+= "**%deregister**\tTo Deregister\n"
            msg_str+= "**%list_participants**\tTo list all participants\n"
            msg_str+= "**%countdown**\tCountdown to Tournament\n"
            msg_str+= "**%annoucement**\tTo see this announcement\n\n"
            msg_str+= "May the RNG be with you!\n"
            msg_str+= "Please pick your fave character now in <#"+self.fightchannel+">\n"
            msg_str+= "(Please contact a Rank 3 if you need to be promoted to Rank 2)\n"
            await self.bot.say(msg_str)
        else:
            await self.bot.say("Tournament is only available for **"+self.getServer(self.fightserver).name+"**, you can join this server here : "+self.invitelink+"")
                
def setup(bot):
    n = War(bot)
    bot.add_cog(n)
