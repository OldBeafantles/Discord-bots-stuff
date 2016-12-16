import discord
from discord.ext import commands
from .utils import checks
import requests
import asyncio
import json
from .utils.dataIO import dataIO
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from math import floor, ceil, sin, cos, pi


#GENERAL SETTINGS
AVAILABLE_LANGUAGES = ["ENGLISH", "FRENCH"]
OWNER_ID = dataIO.load_json("data/red/settings.json")["OWNER"]
LINK = "https://myanimelist.net/profile/"
DATA = "data/mal/"
FONT = "exo2medium.ttf"
PICTURE_FORMAT = "png"
OPENING_METHOD = "RGBA"


#MAL PRESENTATION SETTINGS

IMAGE_WIDTH = 1400
IMAGE_HEIGHT = 1008
HIGH_FONT_SIZE = floor(IMAGE_WIDTH / 18)
MEDIUM_FONT_SIZE = floor(IMAGE_WIDTH / 28)
LITTLE_FONT_SIZE =floor(IMAGE_WIDTH / 36)
WIDTH_AVATAR = floor(IMAGE_WIDTH / 3.5)
HEIGHT_AVATAR = floor(IMAGE_WIDTH / 3.5)
X_AVATAR = floor(IMAGE_WIDTH / 55)
Y_AVATAR = floor(IMAGE_HEIGHT / 55)
#----------------------
X_NAME = WIDTH_AVATAR + X_AVATAR + floor(IMAGE_WIDTH * 0.005)
Y_NAME = floor(IMAGE_HEIGHT / 7) + Y_AVATAR
#----------------------
ALIGNEMENT_X_RIGHT = floor(IMAGE_WIDTH / 1.005)
Y_LAST_ONLINE = floor(IMAGE_HEIGHT * 0.01)
ESPACEMENT_Y_RIGHT = floor(0.055 * IMAGE_HEIGHT)
#----------------------
#----------------------
Y_BEGIN_GLOBAL_INFOS = Y_AVATAR + HEIGHT_AVATAR + floor(0.01 * IMAGE_HEIGHT)
GLOBAL_INFOS_ESPACEMENT = floor(IMAGE_HEIGHT / 22)
ALIGNEMENT_X_GLOBAL_INFOS = floor(WIDTH_AVATAR / 2) + X_AVATAR
#----------------------
#----------------------
WIDTH_GENDER = floor(IMAGE_WIDTH / 15)
HEIGHT_GENDER = floor(IMAGE_HEIGHT / 15)
X_GENDER = floor((X_AVATAR + WIDTH_AVATAR) / 2) - floor(WIDTH_GENDER / 2) 
#----------------------

def initialized(channelID : str):
    
    return channelID in dataIO.load_json("data/mal/settings.json")



def is_admin(userID : str, serverID : str):
    
    return userID == OWNER_ID or userID == dataIO.load_json("data/mal/settings.json")[serverID]["ADMIN"]



def is_mod(userID : str, serverID : str):
    
    return is_admin(userID, serverID) or userID in dataIO.load_json("data/mal/settings.json")[serverID]["MODS"]



def get_MAL_infos(data : str):

    dataDict = {}

    begin = 0
    end = len(data) - 1
    
    #NAME
    #---------------------------
    begin = data.find("<title>")
    end = data[begin:].find(";s Profile - MyAnimeList.net\n") + begin

    dataDict["name"] = data[begin:end][8:-5]

    data = data[end:]
    #---------------------------


    #AVATAR
    #---------------------------
    begin = data.find('<div class="user-image mb8">\n')
    end = data[begin:].find("</div>\n") + begin

    if "No Picture" not in data[begin:end]:
        dataDict["avatar"] = data[begin:end][49:-9]
    else:
        dataDict["avatar"] = "DEFAULT_AVATAR"

    data = data[end:]
    #---------------------------


    #LAST ONLINE
    #---------------------------
    begin = data.find('user-status-title')
    end = data[begin:].find("</li>") + begin

    if "-r online" in data[begin:end]:
        dataDict["last online"] = data[begin:end][102:-7]
    else:
        dataDict["last online"] = data[begin:end][95:-7]
    
    data = data[end:]
    #---------------------------


    #GENDER
    #---------------------------
    begin = data.find('user-status-title')
    end = data[begin:].find("</li>") + begin

    if "Gender" in data[begin:end]:
        dataDict["gender"] = data[begin:end][90:-7]
        data = data[end:]
    else:
        dataDict["gender"] = "UNKNOWN"
    
    #---------------------------


    #BIRTHDATE
    #---------------------------
    begin = data.find('user-status-title')
    end = data[begin:].find("</li>") + begin

    if "Birthday" in data[begin:end]:
        dataDict["birthday"] = data[begin:end][92:-7]
        data = data[end:]
    else:
        dataDict["birthday"] = "UNKNOWN"
    
    #---------------------------


    #LOCATION
    #---------------------------
    begin = data.find('user-status-title')
    end = data[begin:].find("</li>") + begin

    if "Location" in data[begin:end]:
        dataDict["location"] = data[begin:end][92:-7]
        data = data[end:]
    else:
        dataDict["location"] = "UNKNOWN"
    
    #---------------------------


    #JOINED
    #---------------------------
    begin = data.find('user-status-title')
    end = data[begin:].find("</li>") + begin

    dataDict["joined"] = data[begin:end][90:-7]
        
    data = data[end:]
    
    #---------------------------


    #FORUM POSTS
    #---------------------------
    begin = data.find('user-status-data')
    end = data[begin:].find("</li>") + begin

    dataDict["forum posts"] = data[begin:end][34:-11]
        
    data = data[end:]
    
    #---------------------------


    #REVIEWS
    #---------------------------
    begin = data.find('user-status-data')
    end = data[begin:].find("</li>") + begin

    dataDict["reviews"] = data[begin:end][34:-11]
        
    data = data[end:]
    
    #---------------------------


    #RECOMMENDATIONS
    #---------------------------
    begin = data.find('user-status-data')
    end = data[begin:].find("</li>") + begin

    dataDict["recommendations"] = data[begin:end][34:-11]
        
    data = data[end:]
    
    #---------------------------


    #BLOG POSTS
    #---------------------------
    begin = data.find('user-status-data')
    end = data[begin:].find("</li>") + begin

    dataDict["blog posts"] = data[begin:end][34:-11]
        
    data = data[end:]
    
    #---------------------------


    #CLUBS
    #---------------------------
    begin = data.find('user-status-data')
    end = data[begin:].find("</li>") + begin

    dataDict["clubs"] = data[begin:end][34:-11]
        
    data = data[end:]
    
    #---------------------------





    #---------------------------------------------------------
    #                     ANIME STATS                        #
    #---------------------------------------------------------


    #DAYS
    #---------------------------
    begin = data.find('fn-grey2 fw-n')
    end = data[begin:].find("</div>") + begin

    dataDict["anime days"] = data[begin:end][28:]
        
    data = data[end:]
    
    #---------------------------


    #MEAN SCORE
    #---------------------------
    begin = data.find('fn-grey2 fw-n')
    end = data[begin:].find("</div>") + begin

    dataDict["anime mean score"] = data[begin:end][34:]
        
    data = data[end:]
    
    #---------------------------


    #WATCHING
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["anime watching"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #COMPLETED
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["anime completed"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #ON-HOLD
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["anime on-hold"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #DROPPED
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["anime dropped"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------



    #PLAN TO WATCH
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["anime ptw"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------
    


    #TOTAL ENTRIES
    #---------------------------
    begin = data.find('Total Entries')
    end = data[begin:].find("</li>") + begin

    dataDict["anime total entries"] = data[begin:end][45:-7]
        
    data = data[end:]
    
    #---------------------------



    #EPISODES
    #---------------------------
    begin = data.find('Episodes')
    end = data[begin:].find("</li>") + begin

    dataDict["anime episodes"] = data[begin:end][40:-7]
        
    data = data[end:]
    
    #---------------------------




    #---------------------------------------------------------
    #                     MANGA STATS                        #
    #---------------------------------------------------------


    #DAYS
    #---------------------------
    begin = data.find('fn-grey2 fw-n')
    end = data[begin:].find("</div>") + begin

    dataDict["manga days"] = data[begin:end][28:]
        
    data = data[end:]
    
    #---------------------------


    #MEAN SCORE
    #---------------------------
    begin = data.find('fn-grey2 fw-n')
    end = data[begin:].find("</div>") + begin

    dataDict["manga mean score"] = data[begin:end][34:]
        
    data = data[end:]
    
    #---------------------------


    #READING
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["manga reading"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #COMPLETED
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["manga completed"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #ON-HOLD
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["manga on-hold"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------


    #DROPPED
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["manga dropped"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------



    #PLAN TO READ
    #---------------------------
    begin = data.find('di-ib fl-r lh10')
    end = data[begin:].find("</span>") + begin

    dataDict["manga ptr"] = data[begin:end][17:]
        
    data = data[end:]
    
    #---------------------------
    


    #TOTAL ENTRIES
    #---------------------------
    begin = data.find('Total Entries')
    end = data[begin:].find("</li>") + begin

    dataDict["manga total entries"] = data[begin:end][45:-7]
        
    data = data[end:]
    
    #---------------------------



    #CHAPTERS
    #---------------------------
    begin = data.find('Chapters')
    end = data[begin:].find("</li>") + begin

    dataDict["manga chapters"] = data[begin:end][40:-7]
        
    data = data[end:]
    
    #---------------------------



    #VOLUMES
    #---------------------------
    begin = data.find('Volumes')
    end = data[begin:].find("</li>") + begin

    dataDict["manga volumes"] = data[begin:end][39:-7]
        
    data = data[end:]
    
    #---------------------------








    #FAVORITE ANIME
    #---------------------------

    temp = data.find('favorites-list')
    if "No favorite" not in data[temp:temp+50]:

        begin = data[temp:].find('background-image:url') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite anime picture"] = data[begin:end][22:-4]

        data = data[end:]

        temp = data.find('<a href')
        begin = data[temp:].find('">') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite anime name"] = data[begin:end][2:]

    else:
        end = temp + 50
        dataDict["favorite anime picture"] = "UNKNOWN"
        dataDict["favorite anime name"] = "UNKNOWN"
        
    data = data[end:]
    
    #---------------------------



    #FAVORITE MANGA
    #---------------------------

    temp = data.find('favorites-list')
    if "No favorite" not in data[temp:temp+50]:

        begin = data[temp:].find('background-image:url') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite manga picture"] = data[begin:end][22:-4]

        data = data[end:]

        temp = data.find('<a href')
        begin = data[temp:].find('">') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite manga name"] = data[begin:end][2:]

    else:
        end = temp + 50
        dataDict["favorite manga picture"] = "UNKNOWN"
        dataDict["favorite manga name"] = "UNKNOWN"
        
    data = data[end:]
    
    #---------------------------



    #FAVORITE CHARACTER
    #---------------------------

    temp = data.find('favorites-list')
    if "No favorite" not in data[temp:temp+50]:

        begin = data[temp:].find('background-image:url') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite character picture"] = data[begin:end][22:-4]

        data = data[end:]

        temp = data.find('<a href')
        begin = data[temp:].find('">') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite character name"] = data[begin:end][2:]

    else:
        end = temp + 50
        dataDict["favorite character picture"] = "UNKNOWN"
        dataDict["favorite character name"] = "UNKNOWN"
        
    data = data[end:]
    
    #---------------------------



    #FAVORITE PEOPLE
    #---------------------------

    temp = data.find('favorites-list')
    if "No favorite" not in data[temp:temp+50]:

        begin = data[temp:].find('background-image:url') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite people picture"] = data[begin:end][22:-4]

        data = data[end:]

        temp = data.find('<a href')
        begin = data[temp:].find('">') + temp
        end = data[begin:].find("</a>") + begin

        dataDict["favorite people name"] = data[begin:end][2:]

    else:
        end = temp + 50
        dataDict["favorite people picture"] = "UNKNOWN"
        dataDict["favorite people name"] = "UNKNOWN"
        
    data = data[end:]
    
    #---------------------------


    return dataDict



def create_MAL_presentation(data : dict, color : tuple, memberID : str, language : str):

    result_page = Image.open(DATA + "fond.png")
    fnt_high = ImageFont.truetype(DATA + FONT, HIGH_FONT_SIZE)
    fnt_medium = ImageFont.truetype(DATA + FONT, MEDIUM_FONT_SIZE)
    fnt_little = ImageFont.truetype(DATA + FONT, LITTLE_FONT_SIZE)

    members_settings = dataIO.load_json("data/mal/members_settings.json") #We load the settings of the members
    languages = dataIO.load_json("data/mal/languages.json")

    if memberID in members_settings and "FONT_COLOR" in members_settings[memberID]:
        color[0] = members_settings[memberID]["FONT_COLOR"][0]
        color[1] = members_settings[memberID]["FONT_COLOR"][1]
        color[2] = members_settings[memberID]["FONT_COLOR"][2]

    sizeGlobalInfos = Y_BEGIN_GLOBAL_INFOS

    d = ImageDraw.Draw(result_page)

    #AVATAR
    #---------------------------

    if data["avatar"] != "DEFAULT_AVATAR":
        avatarReq = requests.get(data["avatar"])
        avatar = Image.open(BytesIO(avatarReq.content))
    else:
        avatar = Image.open(DATA + "default_avatar.png")

    avatar = avatar.resize(size=(WIDTH_AVATAR,HEIGHT_AVATAR))
    result_page.paste(avatar,(X_AVATAR,Y_AVATAR))

    #NAME
    #---------------------------

    d.text((X_NAME,Y_NAME), data["name"], font=fnt_high, fill=(color[0],color[1],color[2],255))

    #LAST ONLINE
    #---------------------------

    d.text((ALIGNEMENT_X_RIGHT - fnt_medium.getsize(languages[language]["LAST ONLINE"] + data["last online"])[0],Y_LAST_ONLINE), languages[language]["LAST ONLINE"] + data["last online"], font=fnt_medium, fill=(color[0],color[1],color[2],255))

    #GENDER
    #---------------------------

    if data["gender"] == "Male":
        gender = Image.open(DATA + "boy.png").convert(OPENING_METHOD)

    elif data["gender"] == "Female":
        gender = Image.open(DATA + "girl.png").convert(OPENING_METHOD)

    elif data["gender"] == "Non-Binary":
        gender = Image.open(DATA + "trap.png").convert(OPENING_METHOD)

    if data["gender"] != "UNKNOWN":
        gender = gender.resize(size=(WIDTH_GENDER,HEIGHT_GENDER))
        result_page.paste(gender,(X_GENDER,sizeGlobalInfos), mask = gender)

        sizeGlobalInfos += HEIGHT_GENDER

    #BIRTHDAY
    #---------------------------

    if data["birthday"] != "UNKNOWN":

        d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["birthday"])[0] / 2),sizeGlobalInfos), data["birthday"], font=fnt_little, fill=(color[0],color[1],color[2],255))

        sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT


    #LOCATION
    #---------------------------

    if data["location"] != "UNKNOWN":

        d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["location"])[0] / 2),sizeGlobalInfos), data["location"], font=fnt_little, fill=(color[0],color[1],color[2],255))
        
        sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT


    #JOINED
    #---------------------------

    d.text((ALIGNEMENT_X_RIGHT - fnt_medium.getsize(languages[language]["JOINED"] + data["joined"])[0],Y_LAST_ONLINE + ESPACEMENT_Y_RIGHT), languages[language]["JOINED"] + data["joined"], font=fnt_medium, fill=(color[0],color[1],color[2],255))


    #FORUM POSTS
    #---------------------------

    d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["forum posts"] + languages[language]["FORUM POSTS"])[0] / 2),sizeGlobalInfos), data["forum posts"] + languages[language]["FORUM POSTS"], font=fnt_little, fill=(color[0],color[1],color[2],255))
    
    sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT

    #REVIEWS
    #---------------------------

    d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["reviews"] + languages[language]["REVIEWS"])[0] / 2),sizeGlobalInfos), data["reviews"] + languages[language]["REVIEWS"], font=fnt_little, fill=(color[0],color[1],color[2],255))

    sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT

    #RECOMMENDATIONS
    #---------------------------

    d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["recommendations"] + languages[language]["RECOMMENDATIONS"])[0] / 2),sizeGlobalInfos), data["recommendations"] + languages[language]["RECOMMENDATIONS"], font=fnt_little, fill=(color[0],color[1],color[2],255))

    sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT

    #BLOG POSTS
    #---------------------------

    d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["blog posts"] + languages[language]["BLOG POSTS"])[0] / 2),sizeGlobalInfos), data["blog posts"] + languages[language]["BLOG POSTS"], font=fnt_little, fill=(color[0],color[1],color[2],255))

    sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT


    #CLLUBS
    #---------------------------

    d.text((ALIGNEMENT_X_GLOBAL_INFOS - floor(fnt_little.getsize(data["clubs"] + languages[language]["CLUBS"])[0] / 2),sizeGlobalInfos), data["clubs"] + languages[language]["CLUBS"], font=fnt_little, fill=(color[0],color[1],color[2],255))

    sizeGlobalInfos += GLOBAL_INFOS_ESPACEMENT




    #--------------------------#
    #        ANIME STATS       #
    #--------------------------#

    CamAnime = Camembert(3.5, (0.0,0.0))
    CamAnime.addPart((255,255,255), 0.25)


    d = ImageDraw.Draw(result_page)

    return result_page



async def send_image(bot, channel : discord.Channel, memberName : str, memberDiscriminator : str, date : str, image):

    link_to_picture = DATA + "temp/" + memberName + "#" + memberDiscriminator + "_" + date + "." + PICTURE_FORMAT
    image.save(link_to_picture, "PNG", quality = 100)

    await bot.send_file(channel, link_to_picture)

    os.remove(link_to_picture)



class Camembert:

    def __init__(self, radius : float, center : tuple):

        self.radius = radius
        self.center = center
        self.last_angle = 0.0
        self.pourcentage = 0.0
        self.image = Image.new("RGB", (ceil(self.radius * 2), ceil(self.radius * 2)), (255,255,255))
        self.draw = ImageDraw.Draw(self.image)


    def addPart(self, color : tuple, pourcentage : float):
        #Pourcentage must be 0.25, not 25 (for 25%)

        newAngle = self.last_angle + pourcentage * 2 * pi

        point = (round(cos(newAngle) * self.radius, 1), round(sin(newAngle) * self.radius, 1))

        self.draw.line((self.center[0], self.center[1], point[0], point[1]), fill = 255)

        self.last_angle = newAngle




class Mal:

    def __init__(self, bot):

        self.bot = bot
        self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings
        self.members_settings = dataIO.load_json("data/mal/members_settings.json") #We load the settings of the members
        self.languages = dataIO.load_json("data/mal/languages.json") #We load the languages




    @commands.command(pass_context=True)
    @checks.is_owner()
    async def init_mal(self,ctx, user : discord.Member):
        """Inits the commands for this server and set default settings"""

        self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

        if ctx.message.server.id not in self.settings:

            if user.id != OWNER_ID:

                self.settings[ctx.message.server.id] = {}
                self.settings[ctx.message.server.id]["LANGUAGE"] = "ENGLISH"
                self.settings[ctx.message.server.id]["ADMIN"] = user.id
                self.settings[ctx.message.server.id]["MODS"] = []

                dataIO.save_json("data/mal/settings.json", self.settings) #We save the data

                await self.bot.say("Done! \o/")

            else:

                await self.bot.say("The admin couldn't be you, my **Master**! :grimacing:")

        else:

            await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["ALREADY_INITIALIZED"])


    @commands.command(pass_context=True)
    async def delete_mal(self, ctx):
        """Disallows the commands for this server"""

        if initialized(ctx.message.server.id) and is_admin(ctx.message.author.id, ctx.message.server.id):

            self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

            del self.settings[ctx.message.server.id]

            dataIO.save_json("data/mal/settings.json", self.settings)

            await self.bot.say("Done! :grimacing:")



    @commands.command(pass_context=True)
    async def settings_mal(self,ctx):
        """Shows the settings of the server"""

        if initialized(ctx.message.server.id) and is_mod(ctx.message.author.id, ctx.message.server.id):

            msg = "`"
            self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

            for setting in self.settings[ctx.message.server.id]:

                msg += setting + ": " + self.settings[ctx.message.server.id][setting] + "\n"

            msg += "`"

            await self.bot.say(msg)



    @commands.command(pass_context=True)
    async def set_mal(self, ctx, setting_name : str, value : str):
        """Sets a new value to the current server's settings"""

        if initialized(ctx.message.server.id) and is_admin(ctx.message.author.id, ctx.message.server.id):

            self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

            if setting_name in self.settings[ctx.message.server.id] and setting_name != "MODS" and setting_name != "ADMIN":

                if setting_name == "LANGUAGE" and value not in AVAILABLE_LANGUAGES:

                    await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["UNAVAILABLE_LANGUAGE"])
                
                else:

                    self.settings[ctx.message.server.id][setting_name] = value

                    dataIO.save_json("data/mal/settings.json", self.settings) #We save the data

                    await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["DATA_SAVED"])

            else:

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["ERROR_NOT_A_SETTING_NAME"])


    @commands.command(pass_context=True)
    async def add_mod(self, ctx, user : discord.Member):
        """Add a member to the mod list"""

        if initialized(ctx.message.server.id) and is_admin(ctx.message.author.id, ctx.message.server.id):

            self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

            if user.id != OWNER_ID and user.id not in self.settings[ctx.message.server.id]["MODS"]:

                self.settings[ctx.message.server.id]["MODS"].append(user.id)

                dataIO.save_json("data/mal/settings.json", self.settings)

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["MOD_PROMOTION"])

            else:

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["ALREADY_MOD_ADMIN_OWNER"])


    @commands.command(pass_context=True)
    async def rem_mod(self, ctx, user : discord.Member):
        """Remove a member from the mod list"""

        if initialized(ctx.message.server.id) and is_admin(ctx.message.author.id, ctx.message.server.id):

            self.settings = dataIO.load_json("data/mal/settings.json") #We load the settings

            if user.id in self.settings[ctx.message.server.id]["MODS"]:

                self.settings.remove(user.id)

                dataIO.save_json("data/mal/settings.json", self.settings)

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["MOD_DEMOTION"])

            else:

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["NOT_EVEN_A_MOD"])


    @commands.command(pass_context=True)
    async def mal(self, ctx, name : str = ""):
        """Searchs for a MAL presentation using the username (Default: your MAL)"""

        if name == "":

            print("TODO")

        else:

            r = requests.get(LINK + name)

            if r.status_code != 404:

                data = get_MAL_infos(r.text)
                await self.bot.say('```python\n' + str(data) + "```")
                color = (ctx.message.author.color.r,ctx.message.author.color.g,ctx.message.author.color.b)
                self.settings = dataIO.load_json("data/mal/settings.json")
                language = self.settings[ctx.message.server.id]["LANGUAGE"]
                try:
                    image = create_MAL_presentation(data, color, ctx.message.author.id, language)
                    await send_image(self.bot, ctx.message.channel, ctx.message.author.name, ctx.message.author.discriminator, str(ctx.message.timestamp)[:-7], image)
                except Exception as e:
                    await self.bot.say(e)
            else:

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["MAL_USER_NOT_FOUND"])





def setup(bot):
    n = Mal(bot)
    bot.add_cog(n)