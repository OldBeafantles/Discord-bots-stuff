import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import asyncio
import textwrap
import os
import math
import aiohttp
import json
from math import *

class Personnage:
    """Classe mère des différents personnages"""
    
    def __init__(self, userid):
        persos = fileIO("data/rpg/Personnages.json", "load")
        self.nom = persos[userid]["nom"]
        self.HP = persos[userid]["HP"]
        self.defense = persos[userid]["defense"]
        self.attaque = persos[userid]["attaque"]
        self.casque = persos[userid]["casque"]
        self.anneau = persos[userid]["anneau"]
        self.arme = persos[userid]["arme"]
        self.ceinture = persos[userid]["ceinture"]
        self.armure = persos[userid]["armure"]
        self.bottes = persos[userid]["bottes"]
        self.amulette = persos[userid]["amulette"]
        self.reputation = persos[userid]["reputation"]
        self.niveau = persos[userid]["niveau"]
        self.experience = persos[userid]["experience"]
        self.combatsGagnés = persos[userid]["combatsGagnés"]
        self.combatsPerdus = persos[userid]["combatsPerdus"]
        self.prime = persos[userid]["prime"]
        self.surnom = persos[userid]["surnom"]
        self.trophées = persos[userid]["trophées"]
        self.classe = persos[userid]["classe"]
        self.etats = persos[userid]["etats"]
        self.pointsDeCaractéristiques = persos[userid]["pointsDeCaractéristiques"]
        self.robustesse = persos[userid]["robustesse"]
        self.force = persos[userid]["force"]
        self.dextérité = persos[userid]["dextérité"]
        self.sagesse = persos[userid]["sagesse"]

    def __presentation__(self):
        msg = "```\n"
        msg += self.nom + "\t Niveau " + str(self.niveau) + "\nRéputation : " + str(self.reputation) + "\nPrime : " + str(self.prime) + "\nClasse : " + self.classe + "\n"
        msg += "```"
        return msg


class Rpg:

    def __init__(self, bot):
        self.bot = bot
        self.masterid = fileIO("data/red/settings.json", "load")["OWNER"]
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        self.classes =  fileIO("data/rpg/Classes.json", "load")
        self.version = "1.0.0"

    @commands.command(pass_context=True)
    async def create_mychar(self,ctx):
        """Starting a new adventure"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id not in self.personnages:
            await self.bot.say("<@" + ctx.message.author.id +">, which name do you want to pick for your character? (Type `cancel` to cancel the installation)")
            name = await self.bot.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
            if name == None or name.content == "cancel":
                await self.bot.say("<@" + ctx.message.author.id + ">, the creation of your character has been cancelled! :grimacing:")
            else:
                if len(name.content) > 19:
                    await self.bot.say("<@" + ctx.message.author.id + ">, please take a name with less than 20 characters!\nThe creation of your character has been cancelled! :grimacing:")
                else:
                    msg = "<@" + ctx.message.author.id +">, which class between the following ones do you want to pick for your character? (Type the corresponding number or `cancel` to cancel the installation)\n\n```\n"
                    self.classes =  fileIO("data/rpg/Classes.json", "load")
                    i = 1
                    for classe in self.classes:
                        msg += str(i) + ") " + classe + "\n"
                        i += 1
                    msg += "```"
                    await self.bot.say(msg)
                    classchosen = await self.bot.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
                    if classchosen == None or classchosen.content == "cancel":
                        await self.bot.say("<@" + ctx.message.author.id + ">, the creation of your character has been cancelled! :grimacing:")
                    else:
                        try:
                            classchosen = int(classchosen.content)
                            if classchosen > 0 and classchosen <= len(self.classes):
                                i = 0
                                for classe in self.classes:
                                    if i == classchosen - 1:
                                        name_class = classe
                                        break
                                    i += 1
                                self.personnages[ctx.message.author.id] = {}
                                self.personnages[ctx.message.author.id]["nom"] = name.content
                                self.personnages[ctx.message.author.id]["HP"] = self.classes[name_class]["HP de base"]
                                self.personnages[ctx.message.author.id]["defense"] = self.classes[name_class]["defense de base"]
                                self.personnages[ctx.message.author.id]["attaque"] = self.classes[name_class]["attaque de base"]
                                self.personnages[ctx.message.author.id]["casque"] = None
                                self.personnages[ctx.message.author.id]["anneau"] = None
                                self.personnages[ctx.message.author.id]["arme"] = None
                                self.personnages[ctx.message.author.id]["ceinture"] = None
                                self.personnages[ctx.message.author.id]["armure"] = None
                                self.personnages[ctx.message.author.id]["bottes"] = None
                                self.personnages[ctx.message.author.id]["amulette"] = None
                                self.personnages[ctx.message.author.id]["reputation"] = 0
                                self.personnages[ctx.message.author.id]["niveau"] = 1
                                self.personnages[ctx.message.author.id]["experience"] = 0
                                self.personnages[ctx.message.author.id]["combatsGagnés"] = 0
                                self.personnages[ctx.message.author.id]["combatsPerdus"] = 0
                                self.personnages[ctx.message.author.id]["prime"] = 0
                                self.personnages[ctx.message.author.id]["surnom"] = ""
                                self.personnages[ctx.message.author.id]["trophées"] = []
                                self.personnages[ctx.message.author.id]["classe"] = name_class
                                self.personnages[ctx.message.author.id]["etats"] = []
                                self.personnages[ctx.message.author.id]["pointsDeCaractéristiques"] = 0
                                self.personnages[ctx.message.author.id]["force"] = 0
                                self.personnages[ctx.message.author.id]["sagesse"] = 0
                                self.personnages[ctx.message.author.id]["robustesse"] = 0
                                self.personnages[ctx.message.author.id]["dextérité"] = 0
                                fileIO("data/rpg/Personnages.json", "save", self.personnages)
                                a = Personnage(ctx.message.author.id)
                                await self.bot.say("Your character has been successfully created \o/ :\n\n" + a.__presentation__())
                            else:
                                await self.bot.say("<@" + ctx.message.author.id + ">, please type a **correct number**!\nThe creation of your character has been cancelled! :grimacing:")
                        except ValueError:
                            await self.bot.say("<@" + ctx.message.author.id + ">, please type a **number**!\nThe creation of your character has been cancelled! :grimacing:")
        else:
            await self.bot.say("You already have a character!")

    @commands.command(pass_context=True)
    async def del_mychar(self,ctx):
        """Delete your character :'("""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await self.bot.say("Are you sure you want to delete your character?\n\n" + a.__presentation__() + "If you want to delete your account, just type `yes`!")
            answer = await self.bot.wait_for_message(timeout = 60,author = ctx.message.author, channel = ctx.message.channel)
            if answer == None:
                await self.bot.say("I don't wanna wait your answer anymore <@" + ctx.message.author.id + ">! :grimacing:")
            else:
                if answer.content == "yes":
                    del self.personnages[ctx.message.author.id]
                    fileIO("data/rpg/Personnages.json", "save", self.personnages)
                    await self.bot.say("Your character has been successfully removed! :sob:")
                else:
                    await self.bot.say("I guess it's a no ¯\_(ツ)_/¯")
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def mychar (self,ctx):
        """Show your character stats"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await self.bot.say(a.__presentation__())
        else:
            await self.bot.say("You don't even have a character! :grimacing:")
    
    @commands.command(pass_context=True)
    async def rename_mychar(self,ctx, *name):
        """Rename your character"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            name = " ".join(name)
            if len(name) > 19:
                await self.bot.say("<@" + ctx.message.author.id + ">, please take a name with less than 20 characters! :grimacing:")
            else:
                self.personnages[ctx.message.author.id]["nom"] = name
                fileIO("data/rpg/Personnages.json", "save", self.personnages)
                await self.bot.say("Your character's name has been successfully changed!")
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

def setup(bot):
    bot.add_cog(Rpg(bot))
