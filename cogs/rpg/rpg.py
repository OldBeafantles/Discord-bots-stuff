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



class Classe:

    def __init__(self, classname):
        classes = fileIO("data/rpg/Classes.json", "load")
        self.name = classname
        self.BaseHP = classes[classname]["Base HP"]
        self.HP_per_level = classes[classname]["HP per level"]
        self.BaseDEF = classes[classname]["Base DEF"]
        self.DEF_per_level = classes[classname]["DEF per level"]
        self.BaseATK = classes[classname]["Base ATK"]
        self.ATK_per_level = classes[classname]["ATK per level"]
        self.description = classes[classname]["description"]
        self.particularites = classes[classname]["particularites"]

    def presentation(self):
        msg = ""
        msg += "" + self.name + "\n===========================\n\n<"
        msg += "Initial HP = " + str(self.BaseHP) + ">\n<"
        msg += "HP per level = " + str(self.HP_per_level) + ">\n<"
        msg += "Initial ATK = " + str(self.BaseATK) + ">\n<"
        msg += "ATK per level = " + str(self.ATK_per_level) + ">\n<"
        msg += "Initial Defense = " + str(self.BaseDEF) + ">\n<"
        msg += "Defense per level = " + str(self.DEF_per_level) + ">\n\n#"
        msg += self.description + "\n\n["
        msg += "Particularities](" + self.particularites + ")\n\n\n\n\n"
        return msg


class Equipement:

    def __init__(self, equipID):
        objets = fileIO("data/rpg/Objets.json", "load")
        self.name = objets[equipID]["name"]
        self.bonus = objets[equipID]["bonus"]
        self.picture = objets[equipID]["picture"]
        self.price = objets[equipID]["price"]
        self.type = objets[equipID]["type"]
        self.level = objets[equipID]["level"]
        self.id = equipID

    def presentation(self):
        msg = self.name + "\n===========================\n\n"
        msg += "[type](" + self.type + ")\n"
        msg += "[level](" + str(self.level) + ")\n"
        msg += "[price](" + str(self.price) + " ☼)\n"
        msg += "#Bonus\n"
        for bonus in self.bonus:
            res = bonus.split(" ")
            msg += "<" + res[0] + " = " + res[1] + ">\n"
        return msg

class Personnage:
    """Classe mère des différents personnages"""
    
    def __init__(self, userid):
        persos = fileIO("data/rpg/Personnages.json", "load")
        self.name = persos[userid]["name"]
        self.HP = persos[userid]["HP"]
        self.DEF = persos[userid]["DEF"]
        self.ATK = persos[userid]["ATK"]
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
        self.inventory = persos[userid]["inventory"]
        self.equipment = persos[userid]["equipment"]
        self.equipment_invent = persos[userid]["equipment_invent"]
        self.creation_date = persos[userid]["creation_date"]
        self.id = userid
            
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

    async def equip(self, bot, author):
        await bot.send_message(author,self.show_equipment())
        await bot.send_message(author,"Please type the number corresponding to the equipment you want to equip, or `cancel` to cancel the equipment process!")
        answer = await bot.wait_for_message(author = author, check=lambda m: m.channel.is_private, timeout= 60)
        if answer == None:
            msg = "I don't want to wait anymore, I cancel the equipment process!"
        elif answer.content == "cancel":
            msg = "Equipment process cancelled!"
        else:
            try:
                answer = int(answer.content) - 1
                if answer >= 0 and answer <= len(self.equipment_invent) - 1:
                    persos = fileIO("data/rpg/Personnages.json", "load")
                    equip = Equipement(self.equipment_invent[answer][0])
                    if self.level >= equip.level:
                        types = {"helmet" : 0, "amulet" : 1, "armor" : 2, "ring" : 3, "belt" : 4, "weapon" : 5, "boots" : 6}
                        temp = self.equipment[types[equip.type]]
                        persos[self.id]["equipment"][types[equip.type]] = equip.id
                        persos[self.id]["equipment_invent"][answer][1] -= 1
                        if persos[self.id]["equipment_invent"][answer][1] == 0:
                            del persos[self.id]["equipment_invent"][answer]
                        if temp != "None":
                            res = -1
                            for i in range (0,len(persos[self.id]["equipment_invent"])):
                                if persos[self.id]["equipment_invent"][0] == temp:
                                    res = i
                                    break
                            if res == -1:
                                persos[self.id]["equipment_invent"].append([temp,1])
                            else:
                                persos[self.id]["equipment_invent"][i][1] += 1
                        fileIO("data/rpg/Personnages.json", "save", persos)
                        msg = "Done!"
                    else:
                        msg = "You don't have the required level to equip this item! :grimacing:"
                else:
                    msg = "Please type a **correct number**! :grimacing:"
            except ValueError:
                msg = "Please type a **number**! :grimacing:"
        await bot.send_message(author,msg)

    async def unequip(self, bot, author):
        if len(self.equipment) == self.equipment.count("None"):
            await bot.send_message(author,"You don't have any equipped item! :'(")
        else:
            msg = "```Markdown\n"
            msg += "Here's your equipment:\n====================\n\n"
            i = 1
            for item in self.equipment:
                if item != "None":
                    equip = Equipement(item)
                    msg += "[" + str(i) + "][" + equip.type + "](" + equip.name + ")\n"
                i += 1
            msg += "```"
            await bot.send_message(author,msg)
            await bot.send_message(author,"Please type the number corresponding to the equipment you want to unequip, or `cancel` to cancel the unequipment process!")
            answer = await bot.wait_for_message(author = author, check=lambda m: m.channel.is_private, timeout= 60)
            if answer == None:
                msg = "I don't want to wait anymore, I cancel the equipment process!"
            elif answer.content == "cancel":
                msg = "Equipment process cancelled!"
            else:
                try:
                    answer = int(answer.content) - 1
                    if self.equipment[answer] != "None":
                        persos = fileIO("data/rpg/Personnages.json", "load")
                        equip = Equipement(self.equipment[answer])
                        res = -1
                        for i in range (0,len(persos[self.id]["equipment_invent"])):
                            if persos[self.id]["equipment_invent"][0] == equip.id:
                                res = i
                                break
                        if res == -1:
                            persos[self.id]["equipment_invent"].append([equip.id,1])
                        else:
                            persos[self.id]["equipment_invent"][res][1] += 1
                        persos[self.id]["equipment"][answer] = "None"
                        fileIO("data/rpg/Personnages.json", "save", persos)
                        msg = "Done."
                    else:
                        msg = "Please type a **correct number**! :grimacing:"
                except ValueError:
                    msg = "Please type a **number**! :grimacing:"
            await bot.send_message(author,msg)


    async def attrib_cpts(self, bot, author, channel):
        if self.CaracPoints != 0:
            msg = "```Markdown\n"
            msg += "You've got " + str(self.CaracPoints) + " caracteristic points\n===============================================\n\n"
            msg += "<Robustness = " + str(self.robustness) + ">\n"
            msg += "<Strength = " + str(self.strength) + ">\n"
            msg += "<Wisdom = " + str(self.wisdom) + ">\n"
            msg += "<Deterity = " + str(self.dexterity) + ">\n\n"
            msg += "#To attrib a x amount of points to a caracteristic, type 'caracteristic_name amount_value'\n\n"
            msg += "#Example : strength 3\n"
            msg += "```"
            await bot.send_message(channel,msg)
            answer = await bot.wait_for_message(timeout=60, author=author, channel=channel)
            if answer != None:
                a = answer.content.split(" ")
                if len(a) == 2:
                    try:
                        value = int(a[1])
                        carac = a[0][0].upper() + a[0][1:]
                        if carac == "Strength" or carac == "Wisdom" or carac == "Dexterity" or carac == "Robustness":
                            if value <= self.CaracPoints:
                                persos = fileIO("data/rpg/Personnages.json", "load")
                                persos[self.id][carac[0].lower() + carac[1:]] += value
                                persos[self.id]["CaracPoints"] -= value
                                fileIO("data/rpg/Personnages.json", "save", persos)
                                msg = "Done!"
                            else:
                                msg = "You don't have that amount of caracteristic points! :grimacing:\nI cancel the caracteristic points attribution process!"
                        else:
                            msg = "Please type a correct caracteristic name! :grimacing:\nI cancel the caracteristic points attribution process!"
                    except ValueError:
                        msg = "You must type a number in second position! :grimacing:\nI cancel the caracteristic points attribution process!"
                else:
                    msg = "The format isn't correct! :grimacing:\nI cancel the caracteristic points attribution process!"
            else:
                msg = "<@" + author.id + ">, I don't want to wait anymore, I cancel the caracteristic points attribution process!"
        else:
            msg = "You don't have any caracteristic points! :grimacing:"
        await bot.send_message(channel,msg)

    def show_inventory(self):
        msg = "```Markdown\n"
        msg += "Here's your stuff:\n====================\n\n"
        if len(self.inventory) != 0:
            for item in self.inventory:
                msg += "[" + item[0] + "](x" + str(item[1]) + ")\n"
        else:
            msg += "No item :'(\n"
        msg += "\n\n#Money " + str(self.money) + " ☼\n"
        msg += "```"
        return msg

    def show_equipment(self):
        msg = "```Markdown\n"
        msg += "Here's your equipment:\n====================\n\n"
        if len(self.equipment) == self.equipment.count("None"):
            msg += "No equipped objects\n\n\n"
        else:
            for item in self.equipment:
                if item != "None":
                    equip = Equipement(item)
                    msg += "[" + equip.type + "](" + equip.name + ")\n"
        msg += "\nHere's your equipment inventory:\n====================\n\n"
        if len(self.equipment_invent) == 0:
            msg += "No equipment stuff :'(\n\n"
        else:
            i = 1
            for item in self.equipment_invent:
                equip = Equipement(item[0])
                msg += "[" + str(i) + "][" + equip.type + "][" + equip.name + " x" + str(item[1]) + "]\n"
                i += 1
        msg += "```"
        return msg

    def set_avatar(self, link):
        try:
            r = requests.get(link)
            img = Image.open(BytesIO(r.content))
            persos = fileIO("data/rpg/Personnages.json", "load")
            persos[self.id]["avatar"] = link
            fileIO("data/rpg/Personnages.json", "save", persos)
            msg = "Your avatar has been successfully updated! :wink:"
        except Exception as e:
            msg = "There's an error : `" + str(e) + "`"
        return msg

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

    def getXP(self, nbXP):
        persos = fileIO("data/rpg/Personnages.json", "load")
        persos[self.id]["EXP"] += nbXP
        niv = self.getLevelXP(persos[self.id]["EXP"])
        gainLevel = niv - persos[self.id]["level"]
        msg = "`You won " + str(nbXP) + " EXP!"
        if niv != persos[self.id]["level"]:
            classe = Classe(self.classe)
            HP_won = classe.HP_per_level*gainLevel
            persos[self.id]["HP"] += HP_won
            ATK_won = classe.ATK_per_level*gainLevel
            persos[self.id]["ATK"] += ATK_won
            DEF_won = classe.DEF_per_level*gainLevel
            persos[self.id]["DEF"] += DEF_won
            persos[self.id]["level"] = niv
            CaracPoints_won = 5*gainLevel
            persos[self.id]["CaracPoints"] += CaracPoints_won
            msg += "\nYou're now level " + str(niv) + "!\n"
            msg += "You won " + str(HP_won) + " HP!\n"
            msg += "You won " + str(ATK_won) + " ATK!\n"
            msg += "You won " + str(DEF_won) + " DEF!\n"
            msg += "You won " + str(CaracPoints_won) + " caracteristic points!\n\n"
        msg+="`"
        fileIO("data/rpg/Personnages.json", "save", persos)
        return msg

    def remove_item(self, item, nb):
        persos = fileIO("data/rpg/Personnages.json", "load")
        res = -1
        for i in range (0,len(self.inventory)):
            if self.inventory[i][0] == item:
                res = i
                break
        if res != -1:
            if nb != - 1 and nb <= 0:
                msg = "Please type a **correct number**! :grimacing:"
            elif nb == - 1:
                del persos[self.id]["inventory"][res]
                fileIO("data/rpg/Personnages.json", "save", persos)
                msg = "Done!"
            else:
                persos[self.id]["inventory"][res][1] -= nb
                if persos[self.id]["inventory"][res][1] <= 0:
                    del persos[self.id]["inventory"][res]
                fileIO("data/rpg/Personnages.json", "save", persos)
                msg = "Done!"
        else:
            msg = "<@" + self.id + "> don't even have this item! :grimacing:"
        return msg

    def give_item(self, item, nb):
        if nb > 0:
            persos = fileIO("data/rpg/Personnages.json", "load")
            res = -1
            for i in range (0,len(self.inventory)):
                if self.inventory[i][0] == item:
                    res = i
                    break
            if res == -1:
                persos[self.id]["inventory"].append([item,nb])
                fileIO("data/rpg/Personnages.json", "save", persos)
            else:
                persos[self.id]["inventory"][res][1] +=nb
                fileIO("data/rpg/Personnages.json", "save", persos)
            msg = "Done!"
        else:
            msg = "Please type a **correct number**! :grimacing:"
        return msg

    def remove_equip(self, itemID, nb):
        persos = fileIO("data/rpg/Personnages.json", "load")
        res = -1
        for i in range (0,len(self.equipment_invent)):
            if self.equipment_invent[i][0] == itemID:
                res = i
                break
        if res != -1:
            if nb != - 1 and nb <= 0:
                msg = "Please type a **correct number**! :grimacing:"
            elif nb == - 1:
                del persos[self.id]["equipment_invent"][res]
                fileIO("data/rpg/Personnages.json", "save", persos)
                msg = "Done!"
            else:
                persos[self.id]["equipment_invent"][res][1] -= nb
                if persos[self.id]["equipment_invent"][res][1] <= 0:
                    del persos[self.id]["equipment_invent"][res]
                fileIO("data/rpg/Personnages.json", "save", persos)
                msg = "Done!"
        else:
            msg = "<@" + self.id + "> don't even have this item! :grimacing:"
        return msg

    def give_equip(self, itemID, nb):
        if nb > 0:
            objets = fileIO("data/rpg/Objets.json", "load")
            if itemID not in objets:
                msg = "This object doesn't even exist"
            else:
                persos = fileIO("data/rpg/Personnages.json", "load")
                res = -1
                for i in range (0,len(self.equipment_invent)):
                    if self.equipment_invent[i][0] == itemID:
                        res = i
                        break
                if res == - 1:
                    persos[self.id]["equipment_invent"].append([itemID,1])
                else:
                    persos[self.id]["equipment_invent"][res][1] +=nb
                fileIO("data/rpg/Personnages.json", "save", persos)
                msg = "Done!"
        else:
            msg = "Please type a **correct number**! :grimacing:"
        return msg

    async def presentation(self, bot):
        fond = "data/rpg/Parchemin.png"
        fond_height = 442
        fond_width = 345
        result = Image.open(fond).convert('RGBA')
        process = Image.new('RGBA', (fond_width, fond_height), (0,0,0))
        for server in bot.servers:
            for member in server.members:
                if member.id == self.id:
                    avatar_url = member.avatar_url
                    break
        avatar_image = Image
        cadre_image = Image.open('data/rpg/cadre.png').convert('RGBA')
        cadre_image = cadre_image.resize(size=(145,145))
        result.paste(cadre_image,(27,87))
        avatar = self.avatar
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

        #Silhouette
        img = Image.open('data/rpg/Silhouette.png').convert("RGBA")
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] > 200 or item[1] > 200 or item[2] > 200:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        img = img.resize(size=(61,139))
        result.paste(img, (70,234), img)

        #Equipement
        i = 0
        places = [[94,235], [94,257], [94,275], [115,288], [94,292], [71,301], [94,357]]
        for equip in self.equipment:
            if equip != "None":
                equipC = Equipement(equip)
                img = Image.open(equipC.picture).convert('RGBA')
                img = img.resize(size=(15,15))
                result.paste(img, (places[i][0],places[i][1]))
            i += 1

        fnt = ImageFont.truetype('data/rpg/Barthowheel Regular.ttf', 30)
        fnt2 = ImageFont.truetype('data/rpg/Minimoon.ttf', 23)
        fnt3 = ImageFont.truetype('data/rpg/Minimoon.ttf', 20)
        name = self.name
        name_width = fnt.getsize(name)[0]
        classe = self.classe
        HP = self.virgule(str(self.HP))
        ATK = self.virgule(str(self.ATK))
        level = self.virgule(str(self.level))
        robustness = self.virgule(str(self.robustness))
        strength = self.virgule(str(self.strength))
        wisdom = self.virgule(str(self.wisdom))
        dexterity = self.virgule(str(self.dexterity))
        reputation = self.virgule(str(self.reputation))
        bounty = self.virgule(str(self.bounty))
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
        self.objets = fileIO("data/rpg/Objets.json", "load")
        self.banlist = fileIO("data/rpg/banlist.json", "load")
        self.version_module = "1.0.0"

    def getMember(self, userid):
        for server in self.bot.servers:
            for member in server.members:
                if member.id == userid:
                    return member

    @commands.command()
    async def version(self):
        """Show the version of the RPG module"""
        await self.bot.say("`Version : " + self.version_module + "`")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def ban(self,ctx, user : discord.Member):
        """Add a member to the blacklist, so he couldn't use the bot anymore"""
        self.banlist = fileIO("data/rpg/banlist.json", "load")
        if user.id not in self.banlist:
            if user.id != self.masterid:
                self.banlist.append(user.id)
                fileIO("data/rpg/banlist.json", "save", self.banlist)
                await self.bot.say("Done.")
            else:
                await self.bot.say("Don't be that funny! :joy:")
        else:
            await self.bot.say("Already done.")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def unban(self,ctx, user : discord.Member):
        """Add a member to the blacklist, so he couldn't use the bot anymore"""
        self.banlist = fileIO("data/rpg/banlist.json", "load")
        if user.id in self.banlist:
            self.banlist.remove(user.id)
            fileIO("data/rpg/banlist.json", "save", self.banlist)
            await self.bot.say("Done.")
        else:
            await self.bot.say("Already done.")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def list_banned(self, ctx):
        """List all the banned members"""
        self.banlist = fileIO("data/rpg/banlist.json", "load")
        msg = "```Markdown\nList of all the banned members\n=====================\n\n"
        cpt = 1
        if len(self.banlist) != 0:
            for memberID in self.banlist:
                member = self.getMember(memberID)
                msg += "[" + str(cpt) + "]("
                if member:
                    msg += member.name + "#" + member.discriminator
                else:
                    msg += "Not in the servers anymore"
                msg += ")\n"
                cpt += 1
            msg += "```"
        else:
            msg = "There's no banned members! \o/"
        await self.bot.say(msg)

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
                                self.personnages[ctx.message.author.id]["guild"] = "None"
                                self.personnages[ctx.message.author.id]["inventory"] = []
                                self.personnages[ctx.message.author.id]["equipment"] = ["None", "None", "None", "None", "None", "None", "None"]
                                self.personnages[ctx.message.author.id]["equipment_invent"] = []
                                self.personnages[ctx.message.author.id]["creation_date"] = str(ctx.message.timestamp)[:-7]
                                if len(ctx.message.author.avatar_url) != 0:
                                    self.personnages[ctx.message.author.id]["avatar"] = ctx.message.author.avatar_url
                                else:
                                    self.personnages[ctx.message.author.id]["avatar"] = "None"
                                fileIO("data/rpg/Personnages.json", "save", self.personnages)
                                await self.bot.say("Your character has been successfully created \o/ :")
                                a = Personnage(ctx.message.author.id)
                                await a.presentation(self.bot)
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
            await a.presentation(self.bot)
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
            await a.presentation(self.bot)
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
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await self.bot.say(a.set_avatar(link))
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def attrib(self,ctx):
        """To set your caracteristic points"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await a.attrib_cpts(self.bot, ctx.message.author, ctx.message.channel)
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def inventory(self,ctx):
        """Show your inventory throuhgh a private message"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await self.bot.send_message(ctx.message.author, a.show_inventory())
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def equipment(self,ctx):
        """Show your inventory throuhgh a private message"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await self.bot.send_message(ctx.message.author, a.show_equipment())
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def equip(self, ctx):
        """To change your equipment"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await a.equip(self.bot, ctx.message.author)
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    async def unequip(self,ctx):
        """To unequip an item"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if ctx.message.author.id in self.personnages:
            a = Personnage(ctx.message.author.id)
            await a.unequip(self.bot, ctx.message.author)
        else:
            await self.bot.say("You don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def give_item(self,ctx, user : discord.Member, item : str, nb : int = 1):
        """Give an amount of an item to a member"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            a = Personnage(user.id)
            await self.bot.say(a.give_item(item,nb))
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def remove_item (self,ctx, user : discord.Member, item : str, nb : int = -1):
        """To remove an amount of an item to a member"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            a = Personnage(user.id)
            await self.bot.say(a.remove_item(item,nb))
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def give_equip(self,ctx, user : discord.Member, itemID : str, nb : int = 1):
        """Give an amount of an equipment to a member"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            a = Personnage(user.id)
            await self.bot.say(a.give_equip(itemID,nb))
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def remove_equip (self,ctx, user : discord.Member, itemID : str, nb : int = -1):
        """To remove an amount of an equipment to a member"""
        self.personnages = fileIO("data/rpg/Personnages.json", "load")
        if user.id in self.personnages:
            a = Personnage(user.id)
            await self.bot.say(a.remove_equip(itemID,nb))
        else:
            await self.bot.say(user.name + " don't even have a character! :grimacing:")

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
                    if value == "[]":
                        value = []
                    else:
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
    async def infos_equip(self, *name):
        """Get infos from a specified equipment"""
        self.objets = fileIO("data/rpg/Objets.json", "load")
        name = " ".join(name)
        if name != "":
            name = name.lower()
            equip = None
            for objet in self.objets:
                if self.objets[objet]["name"].lower() == name:
                    equip = Equipement(objet)
                    break
            if equip != None:
                msg = "```Markdown\n"
                msg += equip.presentation()
                msg += "```"
                await self.bot.say(msg)
            else:
                await self.bot.say("There's no such equipment...") 
        else:
            await self.bot.say("Please type an equipment name! :grimacing:")


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
                    a = Classe(classe)
                    msg += a.presentation()
            else:
                a = Classe(name)
                msg += a.presentation()
            msg += "```"
            await self.bot.say(msg)

def setup(bot):
    bot.add_cog(Rpg(bot))
