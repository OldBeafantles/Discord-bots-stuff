import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from .utils import checks
import asyncio
import textwrap
import os
import math
import json
from math import *
from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO
import requests





class Personnage:
    """Classe mère des différents personnages"""
    
    def __init__(self, userid):
        persos = fileIO("data/rpg/Personnages.json", "load")
        self.name = persos[userid]["name"]
        self.HP = persos[userid]["HP"]
        self.DEF = persos[userid]["DEF"]
        self.ATK = persos[userid]["ATK"]
        self.helmet = persos[userid]["helmet"]
        self.ring = persos[userid]["ring"]
        self.weapon = persos[userid]["weapon"]
        self.belt = persos[userid]["belt"]
        self.armor = persos[userid]["armor"]
        self.boots = persos[userid]["boots"]
        self.amulet = persos[userid]["amulet"]
        self.reputation = persos[userid]["reputation"]
        self.level = persos[userid]["level"]
        self.EXP = persos[userid]["EXP"]
        self.WonFights = persos[userid]["WonFights"]
        self.LostFights = persos[userid]["LostFights"]
        self.bounty = persos[userid]["bounty"]
        self.nickname = persos[userid]["nickname"]
        self.trophies = persos[userid]["trophies"]
        self.classe = persos[userid]["class"]
        self.states = persos[userid]["states"]
        self.CaracPoints = persos[userid]["CaracPoints"]
        self.robustness = persos[userid]["robustness"]
        self.strength = persos[userid]["strength"]
        self.dexterity = persos[userid]["dexterity"]
        self.wisdom = persos[userid]["wisdom"]
        self.money = persos[userid]["money"]
        self.skill = persos[userid]["skill"]
        self.guild = persos[userid]["guild"]
        self.avatar = persos[userid]["avatar"]
            
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

    def getLevelXP(self,nbXP):
        if nbXP < 10 and nbXP >= 0:
            return 1
        xpdeb = 0
        xpfin = 10
        xpPer = 10
        for i in range(2,500):
            xpfin += ceil(1.5*xpPer)
            xpdeb += xpPer
            xpPer = xpfin - xpdeb
            if nbXP < xpfin and nbXP >= xpdeb:
                return i
        return 500

    def getXP(self, nbXP, userid):
        persos = fileIO("data/rpg/Personnages.json", "load")
        persos[userid]["EXP"] += nbXP
        niv = self.getLevelXP(persos[userid]["EXP"])
        gainLevel = niv - persos[userid]["level"]
        msg = "`You won " + str(nbXP) + " EXP!"
        if niv != persos[userid]["level"]:
            classes = fileIO("data/rpg/Classes.json", "load")
            classe = persos[userid]["class"]
            HP_won = classes[classe]["HP per level"]*gainLevel
            persos[userid]["HP"] += HP_won
            ATK_won = classes[classe]["ATK per level"]*gainLevel
            persos[userid]["ATK"] += ATK_won
            DEF_won = classes[classe]["DEF per level"]*gainLevel
            persos[userid]["DEF"] += DEF_won
            persos[userid]["level"] = niv
            CaracPoints_won = 5*gainLevel
            persos[userid]["CaracPoints"] += CaracPoints_won
            msg += "\nYou're now level " + str(niv) + "!\n"
            msg += "You won " + str(HP_won) + " HP!\n"
            msg += "You won " + str(ATK_won) + " ATK!\n"
            msg += "You won " + str(DEF_won) + " DEF!\n"
            msg += "You won " + str(CaracPoints_won) + " caracteristic points!\n\n"
        msg+="`"
        fileIO("data/rpg/Personnages.json", "save", persos)
        return msg

    async def presentation(self, userid, bot):
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
        avatar = fileIO("data/rpg/Personnages.json", "load")[userid]["avatar"]
        if avatar != "None":
            try:
                r = requests.get(avatar)
                avatar_image = Image.open(BytesIO(r.content))
            except Exception as e:
                await self.bot.say("There's an error : `" + str(e) + "`")
        else:
            avatar_image = Image.open('data/rpg/avatar.png').convert('RGBA')
        avatar_image = avatar_image.resize(size=(120,120))
        result.paste(avatar_image, (39,100))
        fnt = ImageFont.truetype('data/rpg/Barthowheel Regular.ttf', 30)
        fnt2 = ImageFont.truetype('data/rpg/Minimoon.ttf', 23)
        fnt3 = ImageFont.truetype('data/rpg/Minimoon.ttf', 20)
        persos = fileIO("data/rpg/Personnages.json", "load")
        name = persos[userid]["name"]
        name_width = fnt.getsize(name)[0]
        classe = persos[userid]["class"]
        HP = self.virgule(str(persos[userid]["HP"]))
        ATK = self.virgule(str(persos[userid]["ATK"]))
        level = self.virgule(str(persos[userid]["level"]))
        robustness = self.virgule(str(persos[userid]["robustness"]))
        strength = self.virgule(str(persos[userid]["strength"]))
        wisdom = self.virgule(str(persos[userid]["wisdom"]))
        dexterity = self.virgule(str(persos[userid]["dexterity"]))
        reputation = self.virgule(str(persos[userid]["reputation"]))
        bounty = self.virgule(str(persos[userid]["bounty"]))
        bounty_width = fnt3.getsize(bounty)[0]
        d = ImageDraw.Draw(result)
        d.text((round(fond_width/2) - round(name_width/2), 40),name, font=fnt, fill=(0,0,0,0))
        d.text((180, 85),classe, font=fnt2, fill=(0,0,0,0))
        d.text((180, 125),"Level " + level, font=fnt2, fill=(0,0,0,0))
        d.text((180, 165),HP + " HP", font=fnt2, fill=(0,255,0,0))
        d.text((180, 205),ATK + " ATK", font=fnt2, fill=(255,0,0,0))
        d.text((180, 250),"ROB : " + robustness, font=fnt3, fill=(77,0,0,0))
        d.text((180, 280),"STR : " + strength, font=fnt3, fill=(255,70,0,0))
        d.text((180, 310),"WIS : " + wisdom, font=fnt3, fill=(136,0,136,0))
        d.text((180, 340),"DEX : " + dexterity, font=fnt3, fill=(0,170,255,0))
        d.text((30, 370),"Reputation : " + reputation, font=fnt3, fill=(0,0,0,0))
        d.text((230 - bounty_width, 370),"Bounty : " + bounty, font=fnt3, fill=(0,0,0,0))
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
    @checks.is_owner()
    async def test(self,ctx, nb : int = 1):
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        a = Personnage(ctx.message.author.id)
        await self.bot.say(a.getXP(nb,ctx.message.author.id))

    @commands.command(pass_context=True)
    async def attrib(self,ctx):
        """To set your caracteristic points"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            if self.personnages[ctx.message.author.id]["CaracPoints"] != 0:
                msg = "```Markdown\n"
                msg += "You've got " + str(self.personnages[ctx.message.author.id]["CaracPoints"]) + " caracteristic points\n==================================================\n\n"
                msg += "<Robustness = " + str(self.personnages[ctx.message.author.id]["robustness"]) + ">\n"
                msg += "<Strength = " + str(self.personnages[ctx.message.author.id]["strength"]) + ">\n"
                msg += "<Wisdom = " + str(self.personnages[ctx.message.author.id]["wisdom"]) + ">\n"
                msg += "<Deterity = " + str(self.personnages[ctx.message.author.id]["dexterity"]) + ">\n\n"
                msg += "#To attrib a x amount of points to a caracteristic, type 'caracteristic_name amount_value'\n\n"
                msg += "#Example : strength 3\n"
                msg += "```"
                await self.bot.say(msg)
                answer = await self.bot.wait_for_message(timeout=60, author=ctx.message.author, channel=ctx.message.channel)
                if answer != None:
                    a = answer.content.split(" ")
                    if len(a) == 2:
                        try:
                            value = int(a[1])
                            carac = a[0][0].upper() + a[0][1:]
                            if carac == "Strength" or carac == "Wisdom" or carac == "Dexterity" or carac == "Robustness":
                                if value <= self.personnages[ctx.message.author.id]["CaracPoints"]:
                                    self.personnages[ctx.message.author.id][carac[0].lower() + carac[1:]] += value
                                    self.personnages[ctx.message.author.id]["CaracPoints"] -= value
                                    fileIO("data/rpg/Personnages.json", "save", self.personnages)
                                    await self.bot.say("Done.")
                                else:
                                    await self.bot.say("You don't have that amount of caracteristic points! :grimacing:\nI cancel the caracteristic points attribution process!")
                            else:
                                await self.bot.say("Please type a correct caracteristic name! :grimacing:\nI cancel the caracteristic points attribution process!")
                        except ValueError:
                            await self.bot.say("You must type a number in second position! :grimacing:\nI cancel the caracteristic points attribution process!")
                    else:
                        await self.bot.say("The format isn't correct! :grimacing:\nI cancel the caracteristic points attribution process!")
                else:
                    await self.bot.say("<@" + ctx.message.author.id + ">, I don't want to wait anymore, I cancel the caracteristic points attribution process!")
            else:
                await self.bot.say("You don't have any caracteristic points! :grimacing:")
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

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
                                self.personnages[ctx.message.author.id]["name"] = name.content
                                self.personnages[ctx.message.author.id]["HP"] = self.classes[name_class]["Base HP"]
                                self.personnages[ctx.message.author.id]["DEF"] = self.classes[name_class]["Base DEF"]
                                self.personnages[ctx.message.author.id]["ATK"] = self.classes[name_class]["Base ATK"]
                                self.personnages[ctx.message.author.id]["helmet"] = None
                                self.personnages[ctx.message.author.id]["ring"] = None
                                self.personnages[ctx.message.author.id]["weapon"] = None
                                self.personnages[ctx.message.author.id]["belt"] = None
                                self.personnages[ctx.message.author.id]["armor"] = None
                                self.personnages[ctx.message.author.id]["boots"] = None
                                self.personnages[ctx.message.author.id]["amulet"] = None
                                self.personnages[ctx.message.author.id]["reputation"] = 0
                                self.personnages[ctx.message.author.id]["level"] = 1
                                self.personnages[ctx.message.author.id]["EXP"] = 0
                                self.personnages[ctx.message.author.id]["WonFights"] = 0
                                self.personnages[ctx.message.author.id]["LostFights"] = 0
                                self.personnages[ctx.message.author.id]["bounty"] = 0
                                self.personnages[ctx.message.author.id]["nickname"] = ""
                                self.personnages[ctx.message.author.id]["trophies"] = []
                                self.personnages[ctx.message.author.id]["class"] = name_class
                                self.personnages[ctx.message.author.id]["states"] = []
                                self.personnages[ctx.message.author.id]["CaracPoints"] = 0
                                self.personnages[ctx.message.author.id]["strength"] = 0
                                self.personnages[ctx.message.author.id]["wisdom"] = 0
                                self.personnages[ctx.message.author.id]["robustness"] = 0
                                self.personnages[ctx.message.author.id]["dexterity"] = 0
                                self.personnages[ctx.message.author.id]["money"] = 0
                                self.personnages[ctx.message.author.id]["skill"] = 100
                                self.personnages[ctx.message.author.id]["guild"] = None
                                if len(ctx.message.author.avatar_url) != 0:
                                    self.personnages[ctx.message.author.id]["avatar"] = ctx.message.author.avatar_url
                                else:
                                    self.personnages[ctx.message.author.id]["avatar"] = "None"
                                fileIO("data/rpg/Personnages.json", "save", self.personnages)
                                await self.bot.say("Your character has been successfully created \o/ :")
                                a = Personnage(ctx.message.author.id)
                                await a.presentation(ctx.message.author.id, self.bot)
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
            await self.bot.say("Are you sure you want to delete your character?")
            a = Personnage(ctx.message.author.id)
            await a.presentation(ctx.message.author.id, self.bot)
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
            await a.presentation(ctx.message.author.id, self.bot)
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
                self.personnages[ctx.message.author.id]["name"] = name
                fileIO("data/rpg/Personnages.json", "save", self.personnages)
                await self.bot.say("Your character's name has been successfully changed!")
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def avatar_mychar(self,ctx, link : str):
        """Set an avatar for your character"""
        try:
            r = requests.get(link)
            img = Image.open(BytesIO(r.content))
            self.personnages = fileIO("data/rpg/Personnages.json", "load")
            self.personnages[ctx.message.author.id]["avatar"] = link
            fileIO("data/rpg/Personnages.json", "save", self.personnages)
            await self.bot.say("Your avatar has been successfully updated! :wink:")
        except Exception as e:
            await self.bot.say("There's an error : `" + str(e) + "`")

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
                    msg += "Initial HP = " + str(self.classes[classe]["Base HP"]) + ">\n<"
                    msg += "HP per level = " + str(self.classes[classe]["HP per level"]) + ">\n<"
                    msg += "Initial ATK = " + str(self.classes[classe]["Base ATK"]) + ">\n<"
                    msg += "ATK per level = " + str(self.classes[classe]["ATK per level"]) + ">\n<"
                    msg += "Initial Defense = " + str(self.classes[classe]["Base DEF"]) + ">\n<"
                    msg += "Defense per level = " + str(self.classes[classe]["DEF per level"]) + ">\n\n#"
                    msg += self.classes[classe]["description"] + "\n\n["
                    msg += "Particularities](" + self.classes[classe]["particularites"] + ")\n\n\n\n\n"
            else:
                msg += "" + name + "\n============================\n\n<"
                msg += "Initial HP = " + str(self.classes[name]["Base HP"]) + ">\n<"
                msg += "HP per level = " + str(self.classes[name]["HP per level"]) + ">\n<"
                msg += "Initial ATK = " + str(self.classes[name]["Base ATK"]) + ">\n<"
                msg += "ATK per level = " + str(self.classes[name]["ATK per level"]) + ">\n<"
                msg += "Initial Defense = " + str(self.classes[name]["Base DEF"]) + ">\n<"
                msg += "Defense per level = " + str(self.classes[name]["DEF per level"]) + ">\n\n#"
                msg += self.classes[name]["description"] + "\n\n["
                msg += "Particularities](" + self.classes[name]["particularites"] + ")\n\n\n\n\n"
            msg += "```"
            await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Rpg(bot))
