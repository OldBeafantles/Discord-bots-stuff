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
from PIL import Image, ImageDraw, ImageFont, ImageColor


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
            
    def virgule(self, nombre):
        resultat = str(nombre)
        compteur=0
        i=0
        while i != len(resultat):
            if compteur==3:
                resultat=resultat[:len(resultat)-i]+","+resultat[len(resultat)-i:]
                compteur=0
            else:
                compteur+=1
            i+=1
        return resultat

    async def __presentation__(self, userid, bot):
        fond = "data/rpg/Parchemin.png"
        fond_height = 442
        fond_width = 345
        result = Image.open(fond).convert('RGBA')
        process = Image.new('RGBA', (fond_width, fond_height), (0,0,0))
        for server in bot.servers:
            for member in server.members:
                if member.id == userid:
                    avatar_url = member.avatar_url
                    break
        avatar_image = Image
        cadre_image = Image.open('data/rpg/cadre.png').convert('RGBA')
        cadre_image = cadre_image.resize(size=(145,145))
        result.paste(cadre_image,(27,87))
        try:
            async with aiohttp.get(avatar_url) as r:
                image = await r.content.read()
            with open('data/rpg/temp_avatar','wb') as f:
                f.write(image)
                success = True
        except Exception as e:
            success = False
            print(e)
        if success:
            if len(avatar_url) == 0:
                avatar_image = Image.open('data/rpg/avatar.png').convert('RGBA')
            else:
                avatar_image = Image.open('data/rpg/temp_avatar').convert('RGBA')
            avatar_image = avatar_image.resize(size=(120,120))
            result.paste(avatar_image, (39,100))
        fnt = ImageFont.truetype('data/rpg/Barthowheel Regular.ttf', 30)
        fnt2 = ImageFont.truetype('data/rpg/Minimoon.ttf', 23)
        fnt3 = ImageFont.truetype('data/rpg/Minimoon.ttf', 20)
        persos = fileIO("data/rpg/Personnages.json", "load")
        name = persos[userid]["nom"]
        name_width = fnt.getsize(name)[0]
        classe = persos[userid]["classe"]
        HP = self.virgule(str(persos[userid]["HP"]))
        ATK = self.virgule(str(persos[userid]["attaque"]))
        niveau = self.virgule(str(persos[userid]["niveau"]))
        robustesse = self.virgule(str(persos[userid]["robustesse"]))
        force = self.virgule(str(persos[userid]["force"]))
        sagesse = self.virgule(str(persos[userid]["sagesse"]))
        dextérité = self.virgule(str(persos[userid]["dextérité"]))
        reputation = self.virgule(str(persos[userid]["reputation"]))
        prime = self.virgule(str(persos[userid]["prime"]))
        prime_width = fnt3.getsize(prime)[0]
        d = ImageDraw.Draw(result)
        d.text((round(fond_width/2) - round(name_width/2), 40),name, font=fnt, fill=(0,0,0,0))
        d.text((180, 85),classe, font=fnt2, fill=(0,0,0,0))
        d.text((180, 125),"Niveau " + niveau, font=fnt2, fill=(0,0,0,0))
        d.text((180, 165),HP + " HP", font=fnt2, fill=(0,255,0,0))
        d.text((180, 205),ATK + " ATK", font=fnt2, fill=(255,0,0,0))
        d.text((130, 250),"Robustness : " + robustesse, font=fnt3, fill=(77,0,0,0))
        d.text((130, 280),"Strenght : " + force, font=fnt3, fill=(255,70,0,0))
        d.text((130, 310),"Wisdom : " + sagesse, font=fnt3, fill=(136,0,136,0))
        d.text((130, 340),"Dexterity : " + dextérité, font=fnt3, fill=(0,170,255,0))
        d.text((30, 370),"Reputation : " + reputation, font=fnt3, fill=(0,0,0,0))
        d.text((230 - prime_width, 370),"Bounty : " + prime, font=fnt3, fill=(0,0,0,0))
        d = ImageDraw.Draw(result)
        result.save('data/rpg/temp.jpg', 'JPEG', quality=100)

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
                                await self.bot.say("Your character has been successfully created \o/ :")
                                a.__presentation__(ctx.message.author.id, self.bot)
                                await self.bot.send_file(ctx.message.channel,'data/rpg/temp.jpg')
                                os.remove('data/rpg/temp.jpg')

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
            await self.bot.say("Are you sure you want to delete your character?")
            a.__presentation__(ctx.message.author.id, self.bot)
            await self.bot.send_file(ctx.message.channel,'data/rpg/temp.jpg')
            os.remove('data/rpg/temp.jpg')
            await self.bot.say("If you want to delete your account, just type `yes`!")
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
            await a.__presentation__(ctx.message.author.id, self.bot)
            await self.bot.send_file(ctx.message.channel,'data/rpg/temp.jpg')
            os.remove('data/rpg/temp.jpg')
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

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def set_char(self,ctx, user : discord.Member, carac : str, *value):
        """Set a caracteristic to a value for a specified member"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            if carac in self.personnages[user.id]:
                value = " ".join(value)
                if str(type(self.personnages[user.id][carac])) == "<class 'int'>":
                    try:
                        value = int(value)
                        self.personnages[user.id][carac] = value
                        fileIO("data/rpg/Personnages.json", "save", self.personnages)
                        await self.bot.say("The caracteristic has been successfully updated!")
                    except ValueError:
                        await self.bot.say("The format of the caracteristic isn't correct! :grimacing:")
                elif str(type(self.personnages[user.id][carac])) == "<class 'list'>":
                    value = value.split("#")
                    try:
                        for entry in value:
                            entry = int(entry)
                    except ValueError:
                        pass
                    self.personnages[user.id][carac] = value
                    fileIO("data/rpg/Personnages.json", "save", self.personnages)
                    await self.bot.say("The caracteristic has been successfully updated!")
                elif str(type(self.personnages[user.id][carac])) == "<class 'str'>":
                    self.personnages[user.id][carac] = value
                    fileIO("data/rpg/Personnages.json", "save", self.personnages)
                    await self.bot.say("The caracteristic has been successfully updated!")
                else:
                    await self.bot.say("The format of the caracteristic isn't correct! :grimacing:")
            else:
                await self.bot.say("Please type a correct caracteristic name! :grimacing:")
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def show_char(self,ctx, user : discord.Member, carac : str):
        """Show a caracteristic of a member's character"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            if carac in self.personnages[user.id]:
                await self.bot.say("Here's what you requested : `" + str(self.personnages[user.id][carac]) + "`")
            else:
                await self.bot.say("Please type a correct caracteristic name! :grimacing:")
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

    @commands.command()
    async def infos_class(self, name : str = ""):
        """Get infos from a specified classe or for all the existing ones"""
        self.classes =  fileIO("data/rpg/Classes.json", "load")
        if name != "":
            name = name[0].upper() + name[1:]
        if name != "" and name not in self.classes:
            await self.bot.say("Please type a **correct** class name! :grimacing:")
        else:
            msg = "```Markdown\n"
            if name == "":
                for classe in self.classes:
                    msg += "" + classe + "\n============================\n\n<"
                    msg += "Initial HP = " + str(self.classes[classe]["HP de base"]) + ">\n<"
                    msg += "HP per_level = " + str(self.classes[classe]["HP par niveau"]) + ">\n<"
                    msg += "Initial ATK = " + str(self.classes[classe]["attaque de base"]) + ">\n<"
                    msg += "ATK per_level = " + str(self.classes[classe]["attaque par niveau"]) + ">\n<"
                    msg += "Initial Defense = " + str(self.classes[classe]["defense de base"]) + ">\n<"
                    msg += "Defense per_level = " + str(self.classes[classe]["defense par niveau"]) + ">\n\n#"
                    msg += self.classes[classe]["description"] + "\n\n["
                    msg += "Particularities](" + self.classes[classe]["particularites"] + ")\n\n\n\n\n"
            else:
                msg += "" + name + "\n============================\n\n<"
                msg += "Initial HP = " + str(self.classes[name]["HP de base"]) + ">\n<"
                msg += "HP per_level = " + str(self.classes[name]["HP par niveau"]) + ">\n<"
                msg += "Initial ATK = " + str(self.classes[name]["attaque de base"]) + ">\n<"
                msg += "ATK per_level = " + str(self.classes[name]["attaque par niveau"]) + ">\n<"
                msg += "Initial Defense = " + str(self.classes[name]["defense de base"]) + ">\n<"
                msg += "Defense per_level = " + str(self.classes[name]["defense par niveau"]) + ">\n\n#"
                msg += self.classes[name]["description"] + "\n\n["
                msg += "Particularities](" + self.classes[name]["particularites"] + ")\n\n\n\n\n"
            msg += "```"
            await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Rpg(bot))
