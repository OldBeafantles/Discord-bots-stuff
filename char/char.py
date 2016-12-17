import discord
from discord.ext import commands
from .utils import checks
import aiohttp
import asyncio
import requests
import json
import re
from .utils.dataIO import dataIO
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO

LINK = "http://optc-db.github.io/common/data/"
LINK_PICTURE = "http://onepiece-treasurecruise.com/wp-content/uploads/f"
VERTICAL_ESPACEMENT = 15
HORIZONTAL_ESPACEMENT = 110
HORIZONTAL_BASE = 25
HORIZONTAL_BASE_PCITURE = 45
VERTICAL_BASE = 130

def virgule(number : int):
    #Convert an int into a proper str (3000000 --> '3,000,000')

    resultat = str(number)
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


def build_image(list_IDS : list, totalResults : int):

    result_page = Image.open("data/char/results.png")
    fnt = ImageFont.truetype("data/char/Minimoon.ttf", 45)
    fnt_medium = ImageFont.truetype("data/char/Minimoon.ttf", 30)

    d = ImageDraw.Draw(result_page)

<<<<<<< HEAD
        self.bot = bot
        self.PMlist = dataIO.load_json("data/char/PMonly.json")
=======
    d.text((100,17), str(totalResults), font=fnt, fill=(255,255,255,255))
>>>>>>> 3edc8f68d75e1a039213f75b53fd2f27aabba258

    for i in range(0,len(list_IDS)):
        if os.path.exists("data/char/faces/" + str(list_IDS[i]) + ".png") == False:
            imageReq = requests.get(LINK_PICTURE + (4 - len(str(list_IDS[i]))) * "0" + str(list_IDS[i]) + ".png")
            image = Image.open(BytesIO(imageReq.content))
        else:
            image = Image.open("data/char/faces/" + str(list_IDS[i]) + ".png")
        image = image.resize(size=(45,45))
        if i%5 == 0:
            d.text((HORIZONTAL_BASE,VERTICAL_BASE + i * VERTICAL_ESPACEMENT), str(i + 1), font=fnt_medium, fill=(255,255,255,255))
            result_page.paste(image,(HORIZONTAL_BASE + HORIZONTAL_BASE_PCITURE, VERTICAL_BASE + i*VERTICAL_ESPACEMENT))
        elif i%5 == 1:
            d.text((HORIZONTAL_BASE + HORIZONTAL_ESPACEMENT,VERTICAL_BASE + (i - 1) * VERTICAL_ESPACEMENT), str(i + 1), font=fnt_medium, fill=(255,255,255,255))
            result_page.paste(image,(HORIZONTAL_BASE + HORIZONTAL_BASE_PCITURE + HORIZONTAL_ESPACEMENT, VERTICAL_BASE + (i - 1)*VERTICAL_ESPACEMENT))
        elif i%5 == 2:
            d.text((HORIZONTAL_BASE + 2 * HORIZONTAL_ESPACEMENT,VERTICAL_BASE + (i - 2) * VERTICAL_ESPACEMENT), str(i + 1), font=fnt_medium, fill=(255,255,255,255))
            result_page.paste(image,(HORIZONTAL_BASE + HORIZONTAL_BASE_PCITURE + 2 * HORIZONTAL_ESPACEMENT, VERTICAL_BASE + (i - 2)*VERTICAL_ESPACEMENT))
        elif i%5 == 3:
            d.text((HORIZONTAL_BASE + 3 * HORIZONTAL_ESPACEMENT,VERTICAL_BASE + (i - 3) * VERTICAL_ESPACEMENT), str(i + 1), font=fnt_medium, fill=(255,255,255,255))
            result_page.paste(image,(HORIZONTAL_BASE + HORIZONTAL_BASE_PCITURE + 3 * HORIZONTAL_ESPACEMENT, VERTICAL_BASE + (i - 3)*VERTICAL_ESPACEMENT))
        else:
            d.text((HORIZONTAL_BASE + 4 * HORIZONTAL_ESPACEMENT,VERTICAL_BASE + (i - 4) * VERTICAL_ESPACEMENT), str(i + 1), font=fnt_medium, fill=(255,255,255,255))
            result_page.paste(image,(HORIZONTAL_BASE + HORIZONTAL_BASE_PCITURE + 4 * HORIZONTAL_ESPACEMENT, VERTICAL_BASE + (i - 4)*VERTICAL_ESPACEMENT))

    d = ImageDraw.Draw(result_page)

    result_page.save("data/char/temp.png", "PNG", quality=100)


class Char:

    def __init__(self, bot):

        self.bot = bot
        self.PMlist = dataIO.load_json("data/char/PMonly.json")




    async def choose_char(self, listNum : list, data : list, channel : discord.Channel, author : discord.Member):
        #Get the ID of a character basing on the a list of IDs
        build_image(listNum[:30],len(listNum))
        msgToDel = await self.bot.send_file(channel, "data/char/temp.png")
        os.remove("data/char/temp.png")
        answer = await self.bot.wait_for_message(author = author, channel = channel, timeout = 60)

        try:
            await self.bot.delete_message(msgToDel)
        except Forbidden:
            await self.bot.send_message(channel, "I don't have permissions to delete a message, it would be proper tho :grimacing:")
            pass
        except HTTPException:
            await self.bot.send_message(channel, "It seems there's some problem with Discord: it's not my fault!")
            pass
        if answer == None:
            return 0
        else:
            try:
                number = int(answer.content)
                if number > 0 and number < len(listNum) + 1:
                    return listNum[number - 1]
                else:
                    return -1
            except ValueError:
                return -2



    def embed_char(self, charNum : int, data : list):
        #Create an embed object using the ID of a character
        
        text = json.loads(data[charNum][:-1])

        
        colours = {"PSY" : "FFD700", "INT" : "DA70D6", "STR" : "FA8072", "QCK" : "87CEFA", "DEX" : "90EE90"}
        
        #Title (Name of the character)
        title = text[0]
        

        #Type
        
        color = discord.Colour(value = int(colours[text[1]], 16))
        
        embed = discord.Embed(title = title, colour = color)
        
        embed.set_author(name = "Beafantles", icon_url = "https://discordapp.com/api/users/151661401411289088/avatars/885f299c00c8765aad38b3ba50d6695d.jpg")
        embed.set_thumbnail(url = "http://onepiece-treasurecruise.com/wp-content/uploads/f" + "0" * (4 - len(str(charNum))) + str(charNum) + ".png")
        embed.add_field(name = "Type", value = text[1], inline = True)

        #Classes
        if type(text[2]) == str:
            classes = text[2].replace('"', '')
        else:
            classes = ", ".join(text[2])
        embed.add_field(name = "Classes", value = classes, inline = True)

        #Stars
        embed.add_field(name = "Stars", value = text[3], inline = True)

        #Cost
        embed.add_field(name = "Cost", value = text[4], inline = True)

        #CMB
        embed.add_field(name = "CMB", value = text[5], inline = True)

        #Slots
        embed.add_field(name = "Slots", value = text[6], inline = True)

        #Max Level
        embed.add_field(name = "Max level", value = text[7], inline = True)

        #EXP to level Max
        embed.add_field(name = "EXP to Max", value = virgule(text[8]), inline = True)

        #LEVEL 1
        embed.add_field(name = "Level 1", value = virgule(text[9]) + " HP / " + virgule(text[10]) + " ATK / " + virgule(text[11]) + " RCV", inline = False)

        #LEVEL MAX
        embed.add_field(name = "Level " + str(text[7]), value = virgule(text[12]) + " HP / " + virgule(text[13]) + " ATK / " + virgule(text[14]) + " RCV", inline = False)

        infos = requests.get(LINK + "details.js")
        text = infos.text
        number = text.find('{')

        #We must convert some parts of the text to convert it into a dict object
        text = text[number+1:-3]
        text = text.replace('special:','"special":')
        text = text.replace('captain:','"captain":')
        text = text.replace('captainNotes:','"captainNotes":')
        text = text.replace('specialName:','"specialName":')
        text = text.replace('specialNotes:','"specialNotes":')
        text = text.replace('specialNote:','"specialNote":')
        text = text.replace('description:','"description":')
        text = text.replace('sailor:','"sailor":')
        text = text.replace('sailorNotes:','"sailorNotes":')

        #The following lines are here because there are some mistakes in the database
        text = text.replace(',\n    },\n','\n    },\n')
        text = text.replace(',\n        ]','\n        ]')
        text = text.replace('],\n            }',']\n            }')
        text = text.replace('], \n            }',']\n            }') #HEHEHE IS THAT A TROLL?! (LINE 6247)
        text = text.replace('},\n        ]','}\n        ]')
        text = text.replace('\\"', "'")

        while re.search("//", text) != None:
            number = re.search("//", text).span()
            maxD = text[number[1]:].find('\n')
            text = text[:number[0]] + text[number[1] + maxD:]


        temp = text.split("},\n")
        temp[0] = '"1": ' + temp[0][temp[0].count('"'):]
        for i in range(1, len(temp)):
            number = temp[i].find(":")
            found = False
            for el in ["description", "specialName", "specialNotes", "sailor"]:
                if el in temp[i][:number]:
                    found = True
                    break
            if found == False:
                nb = temp[i][:number].count(" ")
                temp[i] = '"' + temp[i][nb:number] + '":' + temp[i][number + 1:]

        temp = "{" + "},\n".join(temp)
        temp = temp[:len(temp) - 6] + "}"
        jsonText = json.loads(temp)

        #Captain ability
        if "captain" in jsonText[str(charNum)]:
            embed.add_field(name = "Captain ability", value = jsonText[str(charNum)]["captain"], inline = False)

        #Special
        if "special" in jsonText[str(charNum)]:
            if type(jsonText[str(charNum)]["special"]) != list:
                if "specialName" in jsonText[str(charNum)]:
                    embed.add_field(name = jsonText[str(charNum)]["specialName"], value = jsonText[str(charNum)]["special"], inline = False)
                else:
                    embed.add_field(name = "Special", value = jsonText[str(charNum)]["special"], inline = False)
                cd = requests.get(LINK + "cooldowns.js")
                cdInfos = cd.text
                cdData = cdInfos.split("\n")
                if "null" not in cdData[charNum]:
                    cdJson = json.loads(cdData[charNum][:-1])
                    if type(cdJson) == list:
                        if cdJson[0] != cdJson[1]:
                            embed.add_field(name = "Cooldown", value = str(cdJson[0]) + " --> " + str(cdJson[1]) + " turns", inline = False)
                        else:
                            embed.add_field(name = "Cooldown", value = str(cdJson[0]) + " turns", inline = False)
                    else:
                        embed.add_field(name = "Cooldown", value = str(cdJson) + " turns", inline = False)
            else:
                cpt = 1
                for spe in jsonText[str(charNum)]["special"]:
                    if type(spe["cooldown"]) != int:
                        if "specialName" in jsonText[str(charNum)]:
                            embed.add_field(name = jsonText[str(charNum)]["specialName"] + ": Step " + str(cpt), value = spe["description"] + "\nCooldown: " + str(spe["cooldown"][0]) + " --> " + str(spe["cooldown"][1]) + " turns", inline = False)
                        else:
                            embed.add_field(name = "Special: Step " + str(cpt), value = spe["description"] + "\nCooldown: " + str(spe["cooldown"][0]) + " --> " + str(spe["cooldown"][1]) + " turns", inline = False)
                    else:
                        if "specialName" in jsonText[str(charNum)]:
                            embed.add_field(name = jsonText[str(charNum)]["specialName"] + ": Step " + str(cpt), value = spe["description"] + "\nCooldown: " + str(spe["cooldown"]) + " turns", inline = False)
                        else:
                            embed.add_field(name = "Special: Step " + str(cpt), value = spe["description"] + "\nCooldown: " + str(spe["cooldown"]) + " turns", inline = False)
                    cpt += 1
        return embed

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def add_PMonly(self, ctx):
        """Add the current channel to the PM only list (to prevent spam)"""
        self.PMlist = dataIO.load_json("data/char/PMonly.json")
        if ctx.message.channel.id in self.PMlist:
            await self.bot.say("This channel is already in the list! :wink:")
        else:
            self.PMlist.append(ctx.message.channel.id)
            dataIO.save_json("data/char/PMonly.json", self.PMlist)
            await self.bot.say("Done!")
            

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def rem_PMonly(self, ctx):
        """Remove the current channel to the PM only list (allow users to spam like hell)"""
        self.PMlist = dataIO.load_json("data/char/PMonly.json")
        if ctx.message.channel.id not in self.PMlist:
            await self.bot.say("This channel wasn't even in the list! :wink:")
        else:
            self.PMlist.remove(ctx.message.channel.id)
            dataIO.save_json("data/char/PMonly.json", self.PMlist)
            await self.bot.say("Done!")


    @commands.command(pass_context = True)
    @checks.is_owner()
    async def list_PMonly(self, ctx):
        """Get the list of the PM only channels of this server"""
        self.PMlist = dataIO.load_json("data/char/PMonly.json")
        list_server_IDS = [[a.id,a.name] for a in ctx.message.server.channels]
        msg = "```css\n"
        for PMonlyID in list_server_IDS:
            if PMonlyID[0] in self.PMlist:
                msg += PMonlyID[1] + "\n"
        msg += "```"
        if msg == "```css\n```":
            await self.bot.say("No channel concerned in this server!")
        else:
            await self.bot.say(msg)


    @commands.command(pass_context=True)
    async def char(self, ctx, *char):
        """Search a character in the github database"""

        list_chars = []

        #That's how we deal with bad typers
        list_chars.append("".join(char).lower())
        list_chars.append("".join(char).upper())
        if "".join(char) not in list_chars:
            list_chars.append("".join(char))
        if " ".join(char) not in list_chars:
            list_chars.append(" ".join(char))
        if " ".join(char).upper() not in list_chars:
            list_chars.append(" ".join(char).upper())
        if " ".join(char).lower() not in list_chars:
            list_chars.append(" ".join(char).lower())

        char_with_spaces = " ".join(char).split(" ")

        txt1 = ""
        txt2 = ""
        for el in char_with_spaces:
            txt1 += el[0].upper() + el[1:] + " "
            txt2 += el[0].lower() + el[1:] + " "

        txt1 = txt1[:-1]
        txt2 = txt2[:-1]

        if txt1 not in list_chars:
            list_chars.append(txt1)
        if txt2 not in list_chars:
            list_chars.append(txt2)



        #Let's get the results now \o/

        request = requests.get(LINK + "aliases.js")

        text = request.text

        count = 0

        list_results = []

        lignes = text.split("\n")

        for ligne in lignes:
            cpt = 0
            found = False
            while found == False and cpt < len(list_chars):
                if list_chars[cpt] in ligne:
                    maxD = ligne.find(": [")
                    list_results.append(int(ligne[:maxD]))
                    found = True
                cpt += 1

        request2 = requests.get(LINK + "units.js")

        text2 = request2.text

        lignes = text2.split("\n")

        for i in range(0, len(lignes)):
            cpt = 0
            found = False
            while found == False and cpt < len(list_chars):
                if list_chars[cpt] in lignes[i] and i not in list_results:
                    list_results.append(i)
                    found = True
                cpt += 1




        data = request2.text.split("\n")

        if len(list_results) == 0:
            await self.bot.say("No result found :grimacing:")

        elif len(list_results) == 1:
            embed = self.embed_char(list_results[0], data)
            self.PMlist = dataIO.load_json("data/char/PMonly.json")
            if ctx.message.channel.id not in self.PMlist:
                await self.bot.send_message(ctx.message.channel, embed = embed)
            else:
                await self.bot.send_message(ctx.message.author, embed = embed)
        else:
            num = await self.choose_char(list_results, data, ctx.message.channel, ctx.message.author)
            if num > 0:
                embed = self.embed_char(num, data)
                self.PMlist = dataIO.load_json("data/char/PMonly.json")
                if ctx.message.channel.id not in self.PMlist:
                    await self.bot.send_message(ctx.message.channel, embed = embed)
                else:
                    await self.bot.send_message(ctx.message.author, embed = embed)
            elif num == 0:
                await self.bot.say("I waited for too long, I cancel the research!")
            elif num == -1:
                await self.bot.say("Please type a **correct** number!")
            else:
                await self.bot.say("Please type a **number**!")


    @commands.command(pass_context=True)
    @checks.is_owner()
    async def update_DB(self, ctx, number1 : int, number2 : int):
        """Update the database"""
        list_errors = []
        list_news = []
        if number2 > number1:
            for i in range(number1,number2 + 1):
                if os.path.exists("data/char/faces/" + str(i) + ".png") == False:
                    imageReq = requests.get(LINK_PICTURE + (4 - len(str(i))) * "0" + str(i) + ".png")
                    if imageReq.status_code != 404:
                        image = Image.open(BytesIO(imageReq.content))
                        image = image.save("data/char/faces/" + str(i) + ".png")
                        list_news.append(i)
                    else:
                        list_errors.append(i)
            msg = "Done!\n`"
            msg += str(len(list_news)) + " new files dowloaded!\n"
            msg += str((number2 - number1) - len(list_news) + 1) + " files were already saved!"
            if len(list_errors) != 0:
                msg += "There are " + str(len(list_errors)) + " errors:\n\n"
                for error in list_errors:
                    msg += str(error) + "\n"
                msg += "\n\nThis is very important to download MANUALLY the characters' faces of the ID above and put them to the folder /data/char/faces (check the syntax to name the picture correctly)!!!\n\nIf you don't understand what I am saying, please contact Beafantles#8917!"
            msg += "`"
            await self.bot.say(msg)
        else:
            await self.bot.say("The second number must be higher than the first one! :grimacing:")


def setup(bot):
    n = Char(bot)
    bot.add_cog(n)
