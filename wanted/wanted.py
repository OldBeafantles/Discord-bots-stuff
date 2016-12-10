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
from copy import copy
from math import *

try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
    pil_available = True
except:
    pil_available = False


class Wanted:

    def __init__(self, bot):
        self.bot = bot
        self.nicks = fileIO("data/wanted/nicks.json","load")
        self.bounties=fileIO("data/wanted/bounties.json","load")
        self.Fbounties=fileIO("data/wanted/Fbounties.json","load")
        self.masterid = fileIO("data/red/settings.json", "load")["OWNER"]
        
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

    
    # Get Bounties
    def getBounty(self, userid):
        self.bounties=fileIO("data/wanted/bounties.json","load")
        self.Fbounties=fileIO("data/wanted/Fbounties.json","load")
        if userid in self.Fbounties:
            return self.Fbounties[userid]
        elif userid in self.bounties:
            return self.bounties[userid]
        else:
            return 0
        


    @commands.command(pass_context=True)
    async def wanted_name(self,ctx, *name):
        """Change name on your wanted poster

           e.g. %wanted_name Ayano 
        """
        self.nicks = fileIO("data/wanted/nicks.json","load")
        name = " ".join(name)
        if len(name)<15:
            self.nicks[ctx.message.author.id] = name
            fileIO("data/wanted/nicks.json","save",self.nicks)
            await self.bot.say("Done!")
        else:
            await self.bot.say("Choose a shorter nickname! (<15 letters)")

    @commands.command(pass_context=True)
    async def register_wanted(self,ctx):
        """So you'll be able to use the wanted feature"""
        self.bounties=fileIO("data/wanted/bounties.json","load")
        self.Fbounties=fileIO("data/wanted/Fbounties.json","load")
        if ctx.message.author.id not in self.bounties and ctx.message.author.id not in self.Fbounties:
            self.bounties[ctx.message.author.id] = 50
            fileIO("data/wanted/bounties.json", "save", self.bounties)
            await self.bot.say("Done.")
        else:
            await self.bot.say("You already used this command before! :wink:")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def fix_bounty(self,ctx,user : discord.Member, nb : int):
        """Fix the bounty of a member"""
        self.bounties=fileIO("data/wanted/bounties.json","load")
        self.Fbounties=fileIO("data/wanted/Fbounties.json","load")
        if ctx.message.author.id in self.bounties:
            del self.bounties[user.id]
            fileIO("data/wanted/bounties.json", "save", self.bounties)
        self.Fbounties[user.id] = nb
        fileIO("data/wanted/Fbounties.json", "save", self.Fbounties)
        await self.bot.say("Done.")

    @commands.command(pass_context=True)
    async def reward(self, ctx, user : discord.Member, nb : int):
        """Reward a member (increasing his bounty)"""
        self.bounties=fileIO("data/wanted/bounties.json","load")
        self.Fbounties=fileIO("data/wanted/Fbounties.json","load")
        if user.id not in self.bounties and user.id not in self.Fbounties:
            await self.bot.say("This member need to use **" + fileIO("data/red/settings.json", "load")["PREFIXES"][0] + "register_wanted** to get this feature!")
        else:
            if user.id in self.Fbounties:
                await self.bot.say("This member has a fixed bounty, I can't do that :grimacing:")
            else:
                if ctx.message.author.id != self.masterid and (nb < 1 or nb > 50000):
                    await self.bot.say("Please type a number between 1 and 50 000!")
                else:
                    self.bounties[user.id] += nb
                    await self.bot.say("Please type a number between 1 and 50 000!")
                    fileIO("data/wanted/bounties.json", "save", self.bounties)
                    await self.bot.say("**" + user.name + "**'s new bounty is now : " + str(self.bounties[user.id]))

    @commands.command(pass_context=True)
    async def wanted(self,ctx, user : discord.Member = None):
        """Show your wanted poster"""
        self.nicks = fileIO("data/wanted/nicks.json","load")
        if not user:
            user = ctx.message.author
        #WANTED POSTER
        if user.id in self.bounties or user.id in self.Fbounties:
            wanted = "data/wanted/wanted.png"
            wanted_heigh = 283
            wanted_width = 200
            result = Image.open(wanted).convert('RGBA')
            process = Image.new('RGBA', (wanted_width,wanted_heigh), (0,0,0))
            #PFP
            avatar_url = user.avatar_url
            avatar_image = Image
            try:
                async with aiohttp.get(avatar_url) as r:
                    image = await r.content.read()
                with open('data/wanted/temp_avatar','wb') as f:
                    f.write(image)
                    success = True
            except Exception as e:
                success = False
                print(e)
            if success:
                if len(avatar_url) == 0:
                    avatar_image = Image.open('data/wanted/avatar.png').convert('RGBA')
                else:
                    avatar_image = Image.open('data/wanted/temp_avatar').convert('RGBA')

                avatar_image = avatar_image.resize(size=(120,120))
                result.paste(avatar_image, (39,63))
            #NAME
            fnt = ImageFont.truetype('data/wanted/western.ttf', 30)
            if user.id not in self.nicks:
                if len(user.name)>14:
                    text = user.name[:14]
                else:
                    text=user.name
                await self.bot.say("Pro tip : If you want a personalized name for your wanted, poster, then just type " + fileIO("data/red/settings.json", "load")["PREFIXES"][0] + "wanted_name name! :wink:")
            else:
                text = self.nicks[user.id]
            text_width = fnt.getsize(text)[0]
            text_heigh = fnt.getsize(text)[1]
            d = ImageDraw.Draw(result)
            d.text((wanted_width/2 - text_width/2,200),text, font=fnt, fill=(0,0,0,0))
            d = ImageDraw.Draw(result)
            #BOUNTY
            fnt2 = ImageFont.truetype('data/wanted/bounty.ttf', 26)
            bounty = self.getBounty(user.id)
            if bounty == 0:
                text2 = "50"
            else:
                text2=self.virgule(bounty)
            text2_width = fnt2.getsize(text2)[0]
            text_heigh = fnt2.getsize(text2)[1]
            d = ImageDraw.Draw(result)
            d.text((wanted_width/2 - text_width/2,200),text, font=fnt, fill=(0,0,0,0))
            d.text(((wanted_width/2 - text2_width/2)+15,225),text2, font=fnt2, fill=(0,0,0,0))
            d = ImageDraw.Draw(result)
            #RESULT
            result.save('data/wanted/temp.jpg','JPEG', quality=100)

            await self.bot.send_file(ctx.message.channel, 'data/wanted/temp.jpg')

            os.remove('data/wanted/temp.jpg')
        else:
            await self.bot.say("This member need to use **" + fileIO("data/red/settings.json", "load")["PREFIXES"][0] + "register_wanted** to get this feature!")
        
            
def setup(bot):
    if pil_available is False:
        raise RuntimeError("Tu n'as pas Pillow d'installe, fais\n```pip3 install pillow```et reessaie")
        return
    bot.add_cog(Wanted(bot))
