import discord
from discord.ext import commands
from .utils import checks
import requests
import asyncio
import json
from .utils.dataIO import dataIO


AVAILABLE_LANGUAGES = ["ENGLISH", "FRENCH"]
OWNER_ID = dataIO.load_json("data/red/settings.json")["OWNER"]
LINK = "https://myanimelist.net/profile/"



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

            print("todo")

        else:

            r = requests.get(LINK + name)

            if r.status_code != 404:

                data = get_MAL_infos(r.text)
                

            else:

                await self.bot.say(self.languages[self.settings[ctx.message.server.id]["LANGUAGE"]]["MAL_USER_NOT_FOUND"])





def setup(bot):
    n = Mal(bot)
    bot.add_cog(n)