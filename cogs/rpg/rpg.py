import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
import asyncio
import textwrap
import os
import json
from math import *
from random import *
#from PIL import Image, ImageDraw, ImageFont, ImageColor
from data.rpg.HUD_Box import *
from PIL import ImageColor #The others needed modules are already imported in HUD_Box
from io import BytesIO
import requests
from datetime import datetime

PATH = "data/rpg/" #The path to the database

#The current version of the RPG module   
VERSION = "1.0.0"

#The factor for EXP points required per level
EXPFACT = 1.5

#Default messages
NO_CHAR_MSG = " don't even have a character! :grimacing:"
NO_PLACE_MSG = " don't have enough place in his inventory for this command! :grimacing:"

def getMember(bot, userID : str):
    #A function that return a discord.Member, corresponding to the ID
    #------------------------------
    #bot : We need the bot ofc!
    #userID : The ID of the member we want to get

    for server in bot.servers:
        for member in server.members:
            if member.id == userID:
                return member


async def check_have_character(bot, channel : discord.Channel, user : discord.Member):
    #A function that check if the user has a character or not
    #------------------------------
    #bot : We need the bot to send the message in case the member doesn't have a character
    #channel : We need to know to which channel the bot will send the message
    #user : The concerned user

    persos = dataIO.load_json("data/rpg/Characters.json")
    if user.id in persos:
        return True
    else:
        await bot.send_message(channel, user.name + "#" + user.discriminator + NO_CHAR_MSG)
        return False

async def check_has_enough_place(bot, channel : discord.Channel, character):
    #A function that check if the user has place in his inventory or not
    #------------------------------
    #bot : We need the bot to send the message in case the member doesn't have a character
    #channel : We need to know to which channel the bot will send the message
    #character : We want to check his inventory (Character class)

    if character.inventory.place >= character.inventory.get_place():
        return True
    else:
        user = getMember(bot, character.id)
        await bot.send_message(channel, user.name + "#" + user.discriminator + NO_PLACE_MSG)
        return False

async def send_temp_image(bot,channel : discord.Channel, image : str):
    #A function that send a picture
    #------------------------------
    #bot : We need the bot to send the picture to Discord
    #channel : We need to know to which channel the bot will send the picture
    #image : the path to the image we want to send

    await bot.send_file(channel, image)
    os.remove(image) #To preserve a clean database \o/



async def no_character_message(bot, channel : discord.Channel):
    #A function that send a cool error message when the member try to get some infos about his character but he doesn't even have one :facepalm:
    #------------------------------
    #bot : We need the bot to send the error message
    #channel : We need to know to which channel the bot will send the message

    msg = MasterBox(minwidth = 5, minheight = 1, overflow = "right")
    TextBox(msg,0,0,5,1,text = YOU_NO_CHAR_MSG)
    await send_temp_image(bot, channel, msg.save("No_char"))


def virgule(number : int):
    #A function that return a str variable from an int, delimited by a ',' caracter every 3 digits --> Example : 3567232 (int) becomes "3,567,232" (str)
    #------------------------------
    #number : The number you want to get the conversion

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


#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                            A class for the Trophies                                       #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Trophie:

    def __init__(self, trophieID : str):

        trophies = dataIO.load_json(PATH + "Trophies.json") #We load the database

        self.id = trophieID
        self.name = trophies[trophieID]["name"]
        self.picture = trophies[trophieID]["picture"]
        self.description = trophies[trophieID]["description"]



#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                                A class for skills                                         #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Skill:

    def __init__(self, skillID : str):
        
        skillsFile = dataIO.load_json(PATH + "Skills.json") #We load the database
        
        #I guess the following attributes are easy to understand :thinking: Otherwise, just check an example of Skill in the database and everything should be clear in your mind
        self.id = skillID                                           #str
        self.name = skillsFile[skillID]["name"]                     #str
        self.types = skillsFile[skillID]["types"]                   #list of str
        self.nbTargetsEn = skillsFile[skillID]["nbTargetEn"]        #int
        self.nbTargetsAl = skillsFile[skillID]["nbTargetAl"]        #int
        self.cooldown = skillsFile[skillID]["cooldown"]             #int
        self.cdInit = skillsFile[skillID]["cdInit"]                 #int
        self.usesPerTurnMax = skillsFile[skillID]["usesPerTurnMax"] #int
        self.energy = skillsFile[skillID]["energy"]                 #int

        self.states = {"allies" : [], "ennemies" : []}              #dict
        for target in skillsFile[skillID]["states"]:
            if skillsFile[skillID]["states"][target] != []:
                for state in skillsFile[skillID]["states"][target]:
                    temp = state.split("#")                         #So we can get all the infos to create a proper State class
                    index = skillsFile[skillID]["types"].index(temp[0]) #To get the corresponding infos in case there's several types 
                    a = State(temp[0],skillsFile[skillID]["type_damage"][index], skillsFile[skillID]["basic_value"][index], skillsFile[skillID]["coeff"][index], skillsFile[skillID]["pourcentage"][index], skillsFile[skillID]["fixed_damage"][index], int(temp[1]), temp[2])
                    self.states[target].append(a) #Then we add the state to the list \o/ YEAH, THAT'S HOW WE DEAL BOI

        self.selfTarget = skillsFile[skillID]["selfTarget"]         #list of booleans
        self.type_damage = skillsFile[skillID]["type_damage"]       #list of str
        self.basic_value = skillsFile[skillID]["basic_value"]       #list of int
        self.coeff = skillsFile[skillID]["coeff"]                   #list of float
        self.pourcentage = skillsFile[skillID]["pourcentage"]       #list of list (every list have 2 'sections' : 1st one is a boolean, 2nd one is a str)
        self.fixed_damage = skillsFile[skillID]["fixed_damage"]     #list of booleans
        self.description = skillsFile[skillID]["description"]       #str

    #launcher : None
    #"targets" : {"ennemies" : [], "allies" : []} <-- The member will need to specify the targets

#-----------------------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                                A class for the IA                                         #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#


class IA:
    
    def __init__(self, IAID : str, targets_type : str):
        IAs = dataIO.load_json(PATH + "IA.json") #We load the database

        self.id = IAID                                          #str
        self.name = IAs[IAID]["name"]                           #str
        self.priorities = IAs[IAID]["priorities"]               #list of str
        self.targets = IAs[IAID]["targets_type"][targets_type]  #the comportment of the IA (depending on the targets who would be chosen)

#-----------------------------------------------------------------------------------------------------------#


#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                    A class for the monsters (grrr grrr)                                   #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Monster:

    def __init__(self, monsterID : str):
        monsters = dataIO.load_json(PATH + "Monsters.json") #We load the database (sounds repetetive now)

        self.id = monsterID                                                                         #str
        self.name = monsters[monsterID]["name"]                                                     #str
        self.font = monsters[monsterID]["font"]                                                     #str
        self.color_font = monsters[monsterID]["color font"]                                         #str (hexadecimal code corresponding to the wanted color)
        self.size_font = monsters[monsterID]["size font"]                                           #int
        self.avatar = monsters[monsterID]["avatar"]                                                 #str
        self.avatar2 = monsters[monsterID]["avatar2"]                                               #str
        self.condition_avatar = monsters[monsterID]["condition avatar"]                             #str
        self.level = randint(monsters[monsterID]["level"][0],monsters[monsterID]["level"][1])       #int
        self.description = monsters[monsterID]["description"]                                       #str
        
        self.baseLVL = monsters[monsterID]["level"][0]                                              #int
        self.baseHP = monsters[monsterID]["Base HP"]                                                #int
        self.baseATK =monsters[monsterID]["Base ATK"]                                               #int
        self.baseDEF = monsters[monsterID]["Base DEF"]                                              #int
        self.baseSTR = monsters[monsterID]["Base STR"]                                              #int
        self.baseDEX = monsters[monsterID]["Base DEX"]                                              #int
        self.baseWIS = monsters[monsterID]["Base WIS"]                                              #int
        self.baseROB = monsters[monsterID]["Base ROB"]                                              #int
        self.baseRESAIR = monsters[monsterID]["Base RES AIR"]                                       #float
        self.baseRESEARTH = monsters[monsterID]["Base RES EARTH"]                                   #float
        self.baseRESFIRE = monsters[monsterID]["Base RES FIRE"]                                     #float
        self.baseRESWATER = monsters[monsterID]["Base RES WATER"]                                   #float
        self.baseENERGY = monsters[monsterID]["Base ENERGY"]                                        #int
        self.baseEXP = monsters[monsterID]["Base EXP"]                                              #int

        self.HP_per_level = monsters[monsterID]["HP per level"]                                     #int
        self.ATK_per_level =monsters[monsterID]["ATK per level"]                                    #int
        self.DEF_per_level = monsters[monsterID]["DEF per level"]                                   #int
        self.STR_per_level = monsters[monsterID]["STR per level"]                                   #int
        self.DEX_per_level = monsters[monsterID]["DEX per level"]                                   #int
        self.WIS_per_level = monsters[monsterID]["WIS per level"]                                   #int
        self.ROB_per_level = monsters[monsterID]["ROB per level"]                                   #int
        self.RESAIR_per_level = monsters[monsterID]["RES AIR per level"]                            #float
        self.RESEARTH_per_level = monsters[monsterID]["RES EARTH per level"]                        #float
        self.RESFIRE_per_level = monsters[monsterID]["RES FIRE per level"]                          #float
        self.RESWATER_per_level = monsters[monsterID]["RES WATER per level"]                        #float
        self.ENERGY_per_level = monsters[monsterID]["ENERGY per level"]                             #int
        self.EXP_per_level = monsters[monsterID]["EXP per level"]                                   #int

        self.maxLVL = monsters[monsterID]["level"][1]                                               #int
        self.maxHP = self.baseHP + (self.maxLVL - 1) * self.HP_per_level                            #int
        self.maxATK = self.baseATK + (self.maxLVL - 1) * self.ATK_per_level                         #int
        self.maxDEF = self.baseDEF + (self.maxLVL - 1) * self.DEF_per_level                         #int
        self.maxSTR = self.baseSTR + (self.maxLVL - 1) * self.STR_per_level                         #int
        self.maxDEX = self.baseDEX + (self.maxLVL - 1) * self.DEX_per_level                         #int
        self.maxWIS = self.baseWIS + (self.maxLVL - 1) * self.WIS_per_level                         #int
        self.maxROB = self.baseROB + (self.maxLVL - 1) * self.ROB_per_level                         #int
        self.maxRESAIR = self.baseRESAIR + (self.maxLVL - 1) * self.RESAIR_per_level                #float
        self.maxRESEARTH = self.baseRESEARTH + (self.maxLVL - 1) * self.RESEARTH_per_level          #float
        self.maxRESFIRE = self.baseRESFIRE + (self.maxLVL - 1) * self.RESFIRE_per_level             #float
        self.maxRESWATER = self.baseRESWATER + (self.maxLVL - 1) * self.RESWATER_per_level          #float
        self.maxENERGY = self.baseENERGY + (self.maxLVL - 1) * self.ENERGY_per_level                #int
        self.maxEXP = self.baseEXP + (self.maxLVL - 1) * self.EXP_per_level                         #int

        self.HP = self.baseHP + self.HP_per_level * (self.level - self.baseLVL)                     #int
        self.ATK = self.baseATK + self.ATK_per_level * (self.level - self.baseLVL)                  #int
        self.DEF = self.baseDEF + self.DEF_per_level * (self.level - self.baseLVL)                  #int
        self.STR = self.baseSTR + self.STR_per_level * (self.level - self.baseLVL)                  #int
        self.DEX = self.baseDEX + self.DEX_per_level * (self.level - self.baseLVL)                  #int
        self.WIS = self.baseWIS + self.WIS_per_level * (self.level - self.baseLVL)                  #int
        self.ROB = self.baseROB + self.ROB_per_level * (self.level - self.baseLVL)                  #int
        self.res_air = self.baseRESAIR + self.RESAIR_per_level * (self.level - self.baseLVL)        #float
        self.res_earth = self.baseRESEARTH + self.RESEARTH_per_level * (self.level - self.baseLVL)  #float
        self.res_fire = self.baseRESFIRE + self.RESFIRE_per_level * (self.level - self.baseLVL)     #float
        self.res_water = self.baseRESWATER + self.RESWATER_per_level * (self.level - self.baseLVL)  #float
        self.energy = self.baseENERGY + self.ENERGY_per_level * (self.level - self.baseLVL)         #int
        self.EXP = self.baseEXP + self.EXP_per_level * (self.level - self.baseLVL)                  #int

        self.current_HP = self.HP                                                                   #int
        self.current_ATK = self.ATK                                                                 #int
        self.current_DEF = self.DEF                                                                 #int
        self.current_STR = self.STR                                                                 #int
        self.current_DEX = self.DEX                                                                 #int
        self.current_WIS = self.WIS                                                                 #int
        self.current_ROB = self.ROB                                                                 #int
        self.current_res_air = self.res_air                                                         #float
        self.current_res_earth = self.res_earth                                                     #float
        self.current_res_fire = self.res_fire                                                       #float
        self.current_res_water = self.res_water                                                     #float
        self.current_energy = self.energy                                                           #int
        
        self.drops = {"equipments" : [], "consumables" : [], "objects" : []}                        #dict

        #We build the Equipments / Consumables / Objects that we could drop
        #item[O] is the ID required to build the classes above
        #item[1] is the pourcentage (%/1000) to drop this item --> 500 = 1/2
        #item[2] is the number of item you can drop --> 2 : You can drop this item twice, once or don't drop it ¯\_(ツ)_/¯
        for item in monsters[monsterID]["drops"]["equipments"]:
            a = Equipment(item[0])
            self.drops["equipments"].append([a,item[1], item[2]])

        for item in monsters[monsterID]["drops"]["consumables"]:
            a = Consumable(item[0])
            self.drops["consumables"].append([a,item[1], item[2]])
        
        for item in monsters[monsterID]["drops"]["objects"]:
            a = Object(item[0])
            self.drops["objects"].append([a,item[1], item[2]])


        self.IA_1 = {}                                                          #dict
        for IA in monsters[monsterID]["IA 1"]:
            self.IA_1[IA] = IA(monsters[monsterID]["IA 1"][IA][0], monsters[monsterID]["IA 1"][IA][1]) #We build the IA using the infos in the database

        self.IA_2 = {}                                                          #dict        
        for IA in monsters[monsterID]["IA 2"]:
            self.IA_2[IA] = []
            for action in monsters[monsterID]["IA 2"][IA]:
                self.IA_2[IA].append(Skill(action[0]), action[1])               #We build the Skill that will be used and we add the dict of the targets corresponding to this Skill

        self.pattern = monsters[monsterID]["pattern"]                           #list of the IA who will be used
        self.conditions = monsters[monsterID]["conditions"]                     #list of the conditions to pass from a IA 1 to another one

        self.skills = []                                                        #list
        for skillID in monsters[monsterID]["skills"]:
            self.skills.append(Skill(skillID))  #We build his spells \o/

    def presentation(self):
        #Return a message with the infos about this monster
        #------------------------------
        #No arguments needed

        msg = self.name
        msg += "===========================\n\n"
        msg += "[Level](" + str(self.baseLVL) + " - " + str(self.maxLVL) +")\n"
        msg += "[HP](" + str(self.baseHP) + " - " + str(self.maxHP) + ")\n"
        msg += "[ATK](" + str(self.baseATK) + " - " + str(self.maxATK) + ")\n"
        msg += "[DEF](" + str(self.baseDEF) + " - " + str(self.maxDEF) + ")\n"
        msg += "[ROB](" + str(self.baseROB) + " - " + str(self.maxROB) + ")\n"
        msg += "[STR](" + str(self.baseSTR) + " - " + str(self.maxSTR) + ")\n"
        msg += "[DEX](" + str(self.baseDEX) + " - " + str(self.maxDEX) + ")\n"
        msg += "[WIS](" + str(self.baseWIS) + " - " + str(self.maxWIS) + ")\n"
        msg += "[RES FIRE](" + str(self.baseRESFIRE) + " % - " + str(self.maxRESFIRE) + " %)\n"
        msg += "[RES EARTH](" + str(self.baseRESEARTH) + " % - " + str(self.maxRESEARTH) + " %)\n"
        msg += "[RES AIR](" + str(self.baseRESAIR) + " % - " + str(self.maxRESAIR) + " %)\n"
        msg += "[RES WATER](" + str(self.baseRESWATER) + " % - " + str(self.maxRESWATER) + " %)\n"
        msg += "[ENERGY](" + str(self.baseENERGY) + " - " + str(self.maxENERGY) + ")\n"
        msg += "[EXP](" + str(self.baseEXP) + " - " + str(self.maxEXP) + ")\n\n"
        msg += "\nDROPS\n===========================\n\n"
        for itemType in self.drops:
            for item in itemType:
                msg += "#" + item.name + "\n"

        msg += "\n\n#" + self.description

        return msg
        


#-----------------------------------------------------------------------------------------------------------#


#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                          A class for the States (not the United ones)                                     #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#
             
class State:

    def __init__(self, typeState : str, typeValue : str, basicValue : int, coeffValue : float, pourcentage : list, fixed_damage : bool, turns : int, when : str):

        self.type = typeState               #str
        self.type_value = typeValue        #str
        self.basicValue = basicValue       #int
        self.coeffValue = coeffValue        #float
        self.pourcentage = pourcentage      #list (1st 'section' : boolean / 2nd 'section' : str)
        self.fixed_damage = fixed_damage    #boolean
        self.turns = turns                  #int
        self.when = when                    #str

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                          A class for the classes (notice the play on words)                               #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Classe:

    def __init__(self, classID : str):

        classes = dataIO.load_json(PATH + "Classes.json") #We load the data


        self.id = classID                                           #str
        self.name = classes[classID]["name"]                        #str
        self.BaseHP = classes[classID]["Base HP"]                   #int
        self.HP_per_level = classes[classID]["HP per level"]        #int
        self.BaseDEF = classes[classID]["Base DEF"]                 #int
        self.DEF_per_level = classes[classID]["DEF per level"]      #int
        self.BaseATK = classes[classID]["Base ATK"]                 #int
        self.ATK_per_level = classes[classID]["ATK per level"]      #int
        self.description = classes[classID]["description"]          #str
        self.particularites = classes[classID]["particularites"]    #str

        self.skills = []                                            #list of list (every of these list have 2 'sections' : 1st one is a Skill class and the 2nd one is an int --> the level needed to obtain this skill)
        for skill in classes[classID]["skills"]:
            self.skills.append([Skill(skill[0]),skill[1]])                   

    def presentation(self):
        #Return a message with the infos about this class
        #------------------------------
        #No arguments needed

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

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                        A class for the inventory                                          #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Inventory:

    def __init__(self, equipment_invent : list, consumable_invent : list, object_invent : list, money : int, ownerPlace : int):

        self.content = [equipment_invent, consumable_invent, object_invent] #list of list of list (2 elements : An Equipment / Consumable / Object class and the owned amount)
        self.money = money                                                  #int
        self.place = ownerPlace                                             #int

    def get_place(self):
        #Return an int corresponding to the place taken by the inventory content
        #------------------------------
        #No arguments needed

        place = 0
        for typeItem in self.content:
            for item in typeItem:
                place += (item[1] // item[0].stack) * item[0].place
        return place

    def show_inventory(self):
        #A function that return a str value, corresponding to your inventory content
        #------------------------------
        #No arguments needed
        msg = "```Markdown\n"
        msg += "Here's your stuff:\n====================\n\n"
        
        total = self.get_place()
        if len(self.content[0]) + len(self.content[1]) + len(self.content[2]) != 0:
            for itemType in self.content: #Your equipment
                if len(itemType) != 0:
                    for item in itemType:
                        place = (item[1] // item[0].stack) * item[0].place
                        msg += "[" + item[0].name + "][x" + str(item[1]) + "][" + str(place) + " places][" + str(round(place/total*100)) + " %]\n"
                else:
                    msg += "No item :'(\n"
                msg += "#-------------------\n\n"
            msg += "\n"

        else:
            msg += "No item :'(\n"
        
        msg += "\n\n#Money " + str(self.money) + " ☼\n"
        msg += "[Place](" + str(total) + "/" + str(self.place) + ")\n"
        msg += "```"

            
        return msg

    def enough_place(self, place : int):
        #Return a bool (True if place >= inventory's place, False otherwise)
        #------------------------------
        #place : an int corresponding to the place we want to check

        return place >= self.get_place()

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                        A class for an Equipment item                                      #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Equipment:

    def __init__(self, equipID : str):

        objets = dataIO.load_json(PATH + "Equipments.json") #We load the data

        self.name = objets[equipID]["name"]                 #str
        self.bonus = objets[equipID]["bonus"]               #list of str
        self.picture = objets[equipID]["picture"]           #str
        self.price = objets[equipID]["price"]               #int
        self.type = objets[equipID]["type"]                 #str
        self.level = objets[equipID]["level"]               #int (the level required to equip this item)
        self.description = objets[equipID]["description"]   #str
        self.sellable = objets[equipID]["sellable"]         #boolean
        self.place = objets[equipID]["place"]               #int
        self.stack = objets[equipID]["stack"]               #int
        self.id = equipID                                   #str

    def presentation(self):
        #Return a message with the infos about this equipment
        #------------------------------
        #No arguments needed

        msg = self.name + "\n===========================\n\n"
        msg += "[type](" + self.type + ")\n"
        msg += "[level](" + str(self.level) + ")\n"
        if self.sellable:
            msg += "[price](" + str(self.price) + " ☼)\n"
        msg += "#Bonus\n"
        for bonus in self.bonus:
            res = bonus.split(" ")
            msg += "<" + res[0] + " = " + res[1] + ">\n"
        msg += "#" + self.description
        return msg

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                        A class for a Consumable item                                      #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Consumable:

    def __init__(self, consumableID : str):

        consumables = dataIO.load_json(PATH + "Consumables.json") #We load the data

        self.name = consumables[consumableID]["name"]               #str
        self.effects = consumables[consumableID]["effects"]         #list of str (with what we need to build State class)
        self.picture = consumables[consumableID]["picture"]         #str
        self.price = consumables[consumableID]["price"]             #int
        self.description = consumables[consumableID]["description"] #str
        self.sellable = consumables[consumableID]["sellable"]       #boolean
        self.place = consumables[consumableID]["place"]             #int
        self.stack = consumables[consumableID]["stack"]             #int
        self.id = consumableID                                      #str

    def presentation(self):
        #Return a message with the infos about this consumable
        #------------------------------
        #No arguments needed

        msg = self.name + "\n===========================\n\n"
        msg += "[effects]"
        for effect in self.effects:
            msg += "(" + effect + ")"
        msg += "\n"
        if self.sellable:
            msg += "[price](" + str(self.price) + " ☼)\n"
        msg += "#" + self.description
        return msg

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                        A class for an Object item                                         #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Object:

    def __init__(self, objectID : str):

        objets = dataIO.load_json(PATH + "Objects.json") #We load the data

        self.name = objets[objectID]["name"]                #str
        self.picture = objets[objectID]["picture"]          #str
        self.price = objets[objectID]["price"]              #int
        self.description = objets[objectID]["description"]  #str
        self.sellable = objets[objectID]["sellable"]        #boolean
        self.place = objets[objectID]["place"]              #int
        self.stack = objets[objectID]["stack"]              #int
        self.id = objectID                                  #str

    def presentation(self):
        #Return a message with the infos about this object
        #------------------------------
        #No arguments needed

        msg = self.name + "\n===========================\n\n"
        if self.sellable:
            msg += "[price](" + str(self.price) + " ☼)\n"
        msg += "#" + self.description
        return msg

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                        A class for the characters                                         #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Character:
    
    def __init__(self, userid : str):
        
        persos = dataIO.load_json(PATH + "Characters.json")  #We load the data

        self.name = persos[userid]["name"]                  #str
        self.classe = Classe(persos[userid]["class"])       #Classe of the character
        self.level = persos[userid]["level"]                #int
        self.HP = self.classe.BaseHP + (self.level - 1) * self.classe.HP_per_level      #int
        self.DEF = self.classe.BaseDEF + (self.level - 1) * self.classe.DEF_per_level   #int
        self.ATK = self.classe.BaseATK + (self.level - 1) * self.classe.ATK_per_level   #int
        self.reputation = persos[userid]["reputation"]      #int
        self.EXP = persos[userid]["EXP"]                    #int
        self.WonFights = persos[userid]["WonFights"]        #int
        self.LostFights = persos[userid]["LostFights"]      #int
        self.bounty = persos[userid]["bounty"]              #int
        self.nickname = persos[userid]["nickname"]          #str

        self.trophies = []                                  #list of Trophie classes (not done yet)
        
        for trophie in persos[userid]["trophies"]:
            self.trophies.append(Trophie(trophie))

        self.states = []                                    #list of State classes
        self.CaracPoints = persos[userid]["CaracPoints"]    #int
        self.SkillPoints = persos[userid]["SkillPoints"]    #int
        self.ROB = persos[userid]["robustness"]             #int
        self.STR = persos[userid]["strength"]               #int
        self.DEX = persos[userid]["dexterity"]              #int
        self.WIS = persos[userid]["wisdom"]                 #int
        self.energy  = persos[userid]["energy"]             #int
        self.equipment = []                                 #list of Equipment classes

        self.max_ROB = self.ROB                             #int
        self.max_WIS = self.WIS                             #int
        self.max_DEX = self.DEX                             #int
        self.max_STR = self.STR                             #int
        self.max_HP = self.HP                               #int
        self.max_DEF = self.DEF                             #int
        self.max_ATK = self.ATK                             #int
        self.max_res_earth = 0.0                            #float
        self.max_res_fire = 0.0                             #float
        self.max_res_water = 0.0                            #float
        self.max_res_air = 0.0                              #float
        self.max_energy = self.energy                       #int

        #We build all the Equipment classes using the ID stocked in the database and we add them to the self.equipement list
        #In case there's no equipment ("None"), we don't build it ofc
        #We also use this opportunity to add the caracteristic bonus of the equipments to the character
        for equip in persos[userid]["equipment"]:
            if equip != "None":
                a = Equipment(equip)
                self.equipment.append(a)
                for bonus in a.bonus:
                    temp = bonus.split(" ")
                    if temp[0] == "ROB":
                        self.max_ROB += int(temp[1])
                    elif temp[0] == "WIS":
                        self.max_WIS += int(temp[1])
                    elif temp[0] == "DEX":
                        self.max_DEX += int(temp[1])
                    elif temp[0] == "STR":
                        self.max_STR += int(temp[1])
                    elif temp[0] == "HP":
                        self.max_HP += int(temp[1])
                    elif temp[0] == "DEF":
                        self.max_DEF += int(temp[1])
                    elif temp[0] == "ATK":
                        self.max_ATK += int(temp[1])
                    elif temp[0] == "RES AIR":
                        self.max_res_air += int(temp[1])
                    elif temp[0] == "RES FIRE":
                        self.max_res_fire += int(temp[1])
                    elif temp[0] == "RES WATER":
                        self.max_res_water += int(temp[1])
                    elif temp[0] == "RES EARTH":
                        self.max_res_earth += int(temp[1])
                    elif temp[0] == "ENERGY":
                        self.max_energy += int(temp[1])
            else:
                self.equipment.append("None")

        self.current_ROB = self.max_ROB                 #int
        self.current_WIS = self.max_WIS                 #int
        self.current_DEX = self.max_DEX                 #int
        self.current_STR = self.max_STR                 #int
        self.current_HP = self.max_HP                   #int
        self.current_DEF = self.max_DEF                 #int
        self.current_ATK = self.max_ATK                 #int
        self.current_res_earth = self.max_res_earth     #float
        self.current_res_fire = self.max_res_fire       #float
        self.current_res_water = self.max_res_water     #float
        self.current_res_air = self.max_res_air         #float
        self.current_energy = self.max_energy           #int
        
        self.money = persos[userid]["money"]            #int
        self.skillpoints = persos[userid]["skill"]      #float
        self.skills = []                                #list of Skill classes
        for skill in self.classe.skills:
            if skill[1] <= self.level:
                self.skills.append(skill[0])
  
        self.guild = persos[userid]["guild"]            #a Guild classe (not done yet)
        self.avatar = persos[userid]["avatar"]          #str
        
        object_invent = []             
        for item in persos[userid]["object_invent"]:
            object_invent.append([Object(item[0]), item[1]])

        consumable_invent = []
        for item in persos[userid]["consumable_invent"]:
            consumable_invent.append([Consumable(item[0]), item[1]])

        equipment_invent = []
        for item in persos[userid]["equipment_invent"]:
            equipment_invent.append([Equipment(item[0]), item[1]])

        self.inventory = Inventory(equipment_invent, consumable_invent, object_invent, self.money, 50 + (self.level - 1) * 10) #Inventory class
        self.creation_date = persos[userid]["creation_date"] #str
        self.id = userid                                     #str        


    def show_equipment(self):
        #A function that return a str value, corresponding to your equipment
        #------------------------------
        #No arguments needed

        msg = "```Markdown\n"
        msg += "Here's your equipment:\n====================\n\n"

        #The equipment items you're wearing
        if len(self.inventory.content[0]) == self.equipment.count("None"):
            msg += "No equipped objects\n\n\n"

        else:
            for item in self.equipment:
                if item != "None":
                    msg += "[" + item.type + "](" + item.name + ")\n"

        msg += "\nHere's your equipment inventory:\n====================\n\n"

        #The equipement items in your inventory
        if len(self.inventory.content[0]) == 0:
            msg += "No equipment stuff :'(\n\n"

        else:
            i = 1
            for item in self.inventory.content[0]:
                msg += "[" + str(i) + "][" + item[0].type + "][" + item[0].name + " x" + str(item[1]) + "]\n"
                i += 1

        msg += "```"

        return msg

    async def equip(self, bot, author : discord.Member):
        #A function that allow you to change your equipment (add an equipment or exchange 2 equipments)
        #------------------------------
        #bot : We need the bot to send messages !
        #author : The concerned member

        if self.inventory.content[0] != []:
            #All this process must be private, that's why we're sending private messages
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
                    if answer >= 0 and answer <= len(self.inventory.content[0]) - 1:

                        persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                        if self.level >= self.inventory.content[0][answer][0].level:
                            
                            #The floowing dict is needed to get the correct index
                            types = {"helmet" : 0, "amulet" : 1, "armor" : 2, "ring" : 3, "belt" : 4, "weapon" : 5, "boots" : 6}
                            temp = self.equipment[types[self.inventory.content[0][answer][0].type]]
                            persos[self.id]["equipment"][types[self.inventory.content[0][answer][0].type]] = self.inventory.content[0][answer][0].id
                            persos[self.id]["equipment_invent"][answer][1] -= 1
                            if persos[self.id]["equipment_invent"][answer][1] == 0:
                                del persos[self.id]["equipment_invent"][answer]
                            #We just removed one unit of the equipment the member choosed to equip from his inventory
                            
                            if temp != "None": #In case of exchanging 2 equipments
                                
                                #We search if the member have the equipment he decided to removed twice. In this case, we just increment the number. Otherwise, we need to create another 'section'
                                res = -1
                                for i in range (0,len(persos[self.id]["equipment_invent"])):
                                    if persos[self.id]["equipment_invent"][i][0].id == temp.id:
                                        res = i
                                        break

                                if res == -1:
                                    persos[self.id]["equipment_invent"].append([temp,1])
                                
                                else:
                                    persos[self.id]["equipment_invent"][res][1] += 1

                            dataIO.save_json(PATH + "Characters.json", persos) #We now can save the data !
                            msg = "Done!"

                        else:
                            msg = "You don't have the required level to equip this item! :grimacing:"
                    
                    else:
                        msg = "Please type a **correct number**! :grimacing:"
                
                except ValueError:
                    msg = "Please type a **number**! :grimacing:"
        
        else:
            msg = "You don't have any equipment object on yourself!"
        
        await bot.send_message(author,msg)

    async def unequip(self, bot, author : discord.Member):
        #A function that allow you to change remove an equipment (it'll be added in your inventory but removed from your equipment)
        #------------------------------
        #bot : We need the bot to send messages !
        #author : The concerned member

        if len(self.equipment) == self.equipment.count("None"): #In case the member doesn't have any equipment!
            await bot.send_message(author,"You don't have any equipped item! :'(")

        else:
            #We show him the equipment he's wearing
            msg = "```Markdown\n"
            msg += "Here's your equipment:\n====================\n\n"
            i = 1
            for item in self.equipment:
                if item != "None":
                    msg += "[" + str(i) + "][" + item.type + "](" + item.name + ")\n"
                i += 1
            msg += "```"

            #All this process must be private, that's why we're sending private messages
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
                    
                    if self.equipment[answer] != "None": #In case, the member typed a correct number \o/
                        
                        persos = dataIO.load_json(PATH + "Characters.json") #We load the data

                        #We search if the member have the equipment he decided to removed twice. In this case, we just increment the number. Otherwise, we need to create another 'section'
                        res = -1
                        for i in range (0,len(persos[self.id]["equipment_invent"])):
                            if persos[self.id]["equipment_invent"][i][0] == self.equipment[answer].id:
                                res = i
                                break
                        if res == -1:
                            persos[self.id]["equipment_invent"].append([self.equipment[answer].id,1])
                        else:
                            persos[self.id]["equipment_invent"][res][1] += 1

                        persos[self.id]["equipment"][answer] = "None" #We remove this equipment :c
                        dataIO.save_json(PATH + "Characters.json", persos) #And we can now save the data!
                        msg = "Done."
                    
                    else:
                        msg = "Please type a **correct number**! :grimacing:"
                
                except ValueError:
                    msg = "Please type a **number**! :grimacing:"
            
            await bot.send_message(author,msg)


    async def attrib_cpts(self, bot, author : discord.Member, channel : discord.Channel):
        #A function that allow you to attrib your caracteristic points
        #------------------------------
        #bot : We need the bot to send messages !
        #author : The concerned member
        #channel : We need to know to which channel will the messages be sent

        if self.CaracPoints != 0:

            #First, the member need to get some infos about his caracteristics and his points
            msg = "```Markdown\n"
            msg += "You've got " + str(self.CaracPoints) + " caracteristic points\n===============================================\n\n"
            msg += "<Robustness = " + str(self.ROB) + ">\n"
            msg += "<Strength = " + str(self.STR) + ">\n"
            msg += "<Wisdom = " + str(self.WIS) + ">\n"
            msg += "<Dexterity = " + str(self.DEX) + ">\n\n"
            msg += "#To attrib a x amount of points to a caracteristic, type 'caracteristic_name amount_value'\n\n"
            msg += "#Example : strength 3\n"
            msg += "```"
            await bot.send_message(channel,msg)


            answer = await bot.wait_for_message(timeout=60, author=author, channel=channel)
            if answer != None:
                a = answer.content.split(" ") #We separate the infos to use them 
                if len(a) == 2:
                    try:
                        value = int(a[1])
                        carac = a[0][0].upper() + a[0][1:] #It's less annoying for the member :D

                        if carac == "Strength" or carac == "Wisdom" or carac == "Dexterity" or carac == "Robustness":
                            if value <= self.CaracPoints:
                                
                                persos = dataIO.load_json(PATH + "Characters.json") #WE LOAD THE DATA!!1!!1!!
                                persos[self.id][carac[0].lower() + carac[1:]] += value
                                persos[self.id]["CaracPoints"] -= value
                                dataIO.save_json(PATH + "Characters.json", persos) #And we save her!
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

    def set_avatar(self, link : str):
        #A function that set your new avatar and returns a str value, corresponding to the answer of the bot
        #------------------------------
        #link : the link of to the picture the member want to set as his new avatar

        try:
            
            #We get the picture
            r = requests.get(link)
            img = Image.open(BytesIO(r.content))

            persos = dataIO.load_json(PATH + "Characters.json") #We load the data
            persos[self.id]["avatar"] = link
            dataIO.save_json(PATH + "Characters.json", persos) #We save the data
            msg = "Your avatar has been successfully updated! :wink:"
        except Exception as e:
            msg = "There's an error : `" + str(e) + "`"
        return msg

    def getLevelXP(self,nbXP : int):
        #A function return the corresponding level according to a EXP amount
        #------------------------------
        #nbXP : the EXP amount you want to know the corresponding level

        if nbXP < 10 and nbXP >= 0:
            return 1

        BeforeXP = 0
        for i in range(2,500):
            BeforeXP += self.getXPforLevel(i)
            if nbXP < BeforeXP:
                return i - 1
        return 500 #The max level \o/

    def getXPforLevel(self, level : int) :
        #Returns the XP amount needed to reach the level
        #------------------------------

        return 10 * (EXPFACT ** (level - 2))

    def getXP(self, nbXP : int):
        #A function that increment your EXP points and handle level passages, returns a str value, corresponding to the answer message
        #------------------------------
        #nbXP : the XP amount that will be incremented to the member character

        persos = dataIO.load_json(PATH + "Characters.json") #We load the data
        persos[self.id]["EXP"] += nbXP                     #We add the EXP amount to the character
        
        #We check how many levels did he won with that EXP won
        niv = self.getLevelXP(persos[self.id]["EXP"])      
        gainLevel = niv - persos[self.id]["level"]

        msg = "`You won " + str(nbXP) + " EXP!"
        
        #We check if there are some news skills 
        skillsLearnt = []
        if niv != persos[self.id]["level"]:
            for skill in self.classe.skills:
                if skill[1] > persos[self.id]["level"] and skill[1] <= niv:
                    skillsLearnt.append(skill[0])

            #Rewards \o/
            HP_won = self.classe.HP_per_level*gainLevel
            persos[self.id]["HP"] += HP_won
            ATK_won = self.classe.ATK_per_level*gainLevel
            persos[self.id]["ATK"] += ATK_won
            DEF_won = self.classe.DEF_per_level*gainLevel
            persos[self.id]["DEF"] += DEF_won
            persos[self.id]["level"] = niv
            CaracPoints_won = 5*gainLevel
            persos[self.id]["CaracPoints"] += CaracPoints_won
            Skillpoints_won = gainLevel
            persos[self.id]["SkillPoints"] += Skillpoints_won

            #The member must be informed!
            msg += "\nYou're now level " + str(niv) + "!\n"
            msg += "You won " + str(HP_won) + " HP!\n"
            msg += "You won " + str(ATK_won) + " ATK!\n"
            msg += "You won " + str(DEF_won) + " DEF!\n"
            msg += "You won " + str(CaracPoints_won) + " caracteristic points!\n"
            msg += "You won " + str(Skillpoints_won) + " skill points!\n"

            if skillsLearnt != []:
                for skill in skillsLearnt:
                    msg += "You learnt a new skill: " + skill.name + "!\n"
        msg+="`"

        dataIO.save_json(PATH + "Characters.json", persos) #We save the data
        
        return msg

    def remove_object(self, itemID : str, nb : int):
        #A function that remove an amount of a specific object from a character's inventory, returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the object you want to remove
        #nb : the amount of this object you want to remove (nb = -1 --> remove completely the object, ignoring the amount owned by the character)

        objects = dataIO.load_json(PATH + "Objects.json") #We load the data
        
        if itemID in objects:
            
            #We check if the character has this object or not
            res = -1
            for i in range (0,len(self.inventory.content[2])):
                if self.inventory.content[2][i][0].id == itemID:
                    res = i
                    break

            if res != -1:

                if nb != - 1 and nb <= 0:
                    msg = "Please type a **correct number**! :grimacing:"
                
                elif nb == - 1:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    del persos[self.id]["object_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
                
                else:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    persos[self.id]["object_invent"][res][1] -= nb
                    if persos[self.id]["object_invent"][res][1] <= 0:
                        del persos[self.id]["object_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
            
            else:
                msg = "<@" + self.id + "> don't even have this item! :grimacing:"
        
        else:
            msg = "This object doesn't even exist! :grimacing:"
        
        return msg

    def give_object(self, itemID : str, nb : int):
        #A function that add an amount of a specific object in a character's inventory, returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the object you want to give
        #nb : the amount of this object you want to give

        objects = dataIO.load_json(PATH + "Objects.json") #We load the data

        if itemID in objects:
            if nb > 0:

                persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                
                #We check if the character has this object or not
                res = -1
                for i in range (0,len(self.inventory.content[2])):
                    if self.inventory.content[2][i][0].id == itemID:
                        res = i
                        break

                if res == -1:
                    persos[self.id]["object_invent"].append([itemID,nb])
                
                else:
                    persos[self.id]["object_invent"][res][1] += nb

                dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                msg = "Done!"
            
            else:
                msg = "Please type a **correct number**! :grimacing:"
        
        else:
            msg = "This object doesn't even exist! :grimacing:"
        
        return msg

    def remove_consumable(self, itemID : str, nb : int):
        #A function that remove an amount of a specific consumable from a character's inventory, returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the consumable you want to remove
        #nb : the amount of this consumable you want to remove (nb = -1 --> remove completely the consumable, ignoring the amount owned by the character)
        
        consumables = dataIO.load_json(PATH + "Consumables.json") #We load the data

        if itemID in consumables:
            
            #We check if the character has this consumable or not
            res = -1
            for i in range (0,len(self.self.inventory.content[1])):
                if self.inventory.content[1][i][0].id == itemID:
                    res = i
                    break

            if res != -1:
                
                if nb != - 1 and nb <= 0:
                    msg = "Please type a **correct number**! :grimacing:"
                
                elif nb == - 1:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    del persos[self.id]["consumable_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
                
                else:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    persos[self.id]["consumable_invent"][res][1] -= nb
                    if persos[self.id]["consumable_invent"][res][1] <= 0:
                        del persos[self.id]["consumable_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
            
            else:
                msg = "<@" + self.id + "> don't even have this item! :grimacing:"
        
        else:
            msg = "This consumable doesn't even exist! :grimacing:"
        
        return msg

    def give_consumable(self, itemID : str, nb : int):
        #A function that add an amount of a specific consumable in a character's inventory (not the equiped items tho), returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the consumable you want to give
        #nb : the amount of this consumable you want to give

        consumables = dataIO.load_json(PATH + "Consumables.json") #We load the data
        
        if itemID in consumables:
            if nb > 0:
                
                persos = dataIO.load_json(PATH + "Characters.json") #We load the data

                #We check if the character has this consumable or not
                res = -1
                for i in range (0,len(self.inventory.content[1])):
                    if self.inventory.content[1][i][0].id == itemID:
                        res = i
                        break

                if res == -1:
                    persos[self.id]["consumable_invent"].append([itemID,nb])
                
                else:
                    persos[self.id]["consumable_invent"][res][1] += nb

                dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                msg = "Done!"
            
            else:
                msg = "Please type a **correct number**! :grimacing:"
        
        else:
            msg = "This consumable doesn't even exist! :grimacing:"
        
        return msg

    def remove_equip(self, itemID : str, nb : int):
        #A function that remove an amount of a specific equipment from a character's inventory, returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the equipment you want to remove
        #nb : the amount of this equipment you want to remove (nb = -1 --> remove completely the consumable, ignoring the amount owned by the character)
        
        equipments = dataIO.load_json(PATH + "Equipments.json") #We load the data

        if itemID in equipments:
           
            #We check if the character has this equipment or not
            res = -1
            for i in range (0,len(self.inventory.content[0])):
                if self.inventory.content[0][i][0].id == itemID:
                    res = i
                    break

            if res != -1:
                
                if nb != - 1 and nb <= 0:
                    msg = "Please type a **correct number**! :grimacing:"
                
                elif nb == - 1:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    del persos[self.id]["equipment_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
                
                else:
                    persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                    persos[self.id]["equipment_invent"][res][1] -= nb
                    if persos[self.id]["equipment_invent"][res][1] <= 0:
                        del persos[self.id]["equipment_invent"][res]
                    dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                    msg = "Done!"
            
            else:
                msg = "<@" + self.id + "> don't even have this item! :grimacing:"
        
        else:
            msg = "This equipment doesn't even exist! :grimacing:"
        
        return msg

    def give_equip(self, itemID : str, nb : int):
        #A function that add an amount of a specific equipment in a character's inventory (not the equiped items tho), returns a str value, corresponding to the answer message
        #------------------------------
        #itemID : The ID of the equipment you want to give
        #nb : the amount of this equipment you want to give

        equipments = dataIO.load_json(PATH + "Equipments.json") #We load the data

        if itemID in equipments:
            if nb > 0:

                persos = dataIO.load_json(PATH + "Characters.json") #We load the data
                
                #We check if the character has this equipment or not
                res = -1
                for i in range (0,len(self.inventory.content[0])):
                    if self.inventory.content[0][i][0].id == itemID:
                        res = i
                        break

                if res == - 1:
                    persos[self.id]["equipment_invent"].append([itemID,1])
                
                else:
                    persos[self.id]["equipment_invent"][res][1] +=nb
                
                dataIO.save_json(PATH + "Characters.json", persos) #We save the data
                msg = "Done!"
            
            else:
                msg = "Please type a **correct number**! :grimacing:"
        
        else:
            msg = "This equipment doesn't even exist! :grimacing:"
        
        return msg


    async def presentation(self, bot, channel : discord.Channel):
        #A function that send a picture of the character \o/ 
        #------------------------------
        #bot : We need the bot to send the picture
        #channel : We need to know to which channel should the picture be sent

        main = MasterBox(minwidth = 11, minheight = 12)

        currentLevelXP = 0
        if self.level != 1:
            for i in range(2, self.level + 1):
                currentLevelXP += self.getXPforLevel(i)

        currentLevelXP = ceil(currentLevelXP)

        BeforeAndNextLevelXP = 0
        for i in range(2, self.level + 2):
            BeforeAndNextLevelXP += self.getXPforLevel(i)

        BeforeAndNextLevelXP = ceil(BeforeAndNextLevelXP)
        #- Head ---------------------------------------------------------------------------------------------------------------------------------------------
        #Age
        TextBox(main, 9, 0, width = 2, height = 1, text = str((datetime.now() - datetime.strptime(self.creation_date, '%Y-%m-%d %H:%M:%S.%f')).days) + " day(s)",
                lines_per_square = 1, font = (FONT[0], 20), justify = "right")

        #Avatar (HP always 100% because current HP are not supposed to be displayed in mychar)
        avatar = self.avatar
        if avatar != "DEFAULT AVATAR":
            try:
                r = requests.get(avatar)
                avatar = BytesIO(r.content)
            except Exception as e:
                await self.bot.say("There's an error : `" + str(e) + "`")
        else:
            avatar = PATH + 'avatar.png'

        AvatarBox(main, 1, 1, 2, 2, image = avatar, maximum = BeforeAndNextLevelXP, minimum = currentLevelXP, current = self.EXP, 
                  line_color = percent_color((0, 255, 0, 255), BeforeAndNextLevelXP, (255, 0, 0, 255), currentLevelXP, self.EXP))

        #Name
        Title(main, 3, 1, width = 8, height = 1, text = self.name)
        #Nickname
        Subtitle(main, 3, 2, width = 4, height = 1, text = self.nickname)
        
        ImageBox(main, 8, 2, width = 2, height = 2, image = PATH + "Images/Avatars/Carotte.png", icon = False, frame = True) #Not finished

        #Level
        Paragraph(main, 1, 3, width = 3, height = 1, text = "LVL : " + virgule(str(self.level)), lines_per_square = 1, font = (FONT[0], 25))
        #Class name
        Paragraph(main, 4, 3, width = 4, height = 1, text = "Class : " + self.classe.name, lines_per_square = 1, font = (FONT[0], 25))
        #Put here job, with lines_per_square = 2 and text = "Class : " + class + "\nJob : " + job
        #XP

        GaugeBox(main, 1, 4, length = 7, orient = "horizontal", maximum = BeforeAndNextLevelXP, minimum = currentLevelXP, current = self.EXP,
                 line_color = percent_color( (0, 105, 234, 255), BeforeAndNextLevelXP, (0, 156, 255, 255), currentLevelXP, self.EXP),
                 name = "XP", name_font = (FONT[0], 25), maximum_text = virgule(self.EXP) + " / " + virgule(BeforeAndNextLevelXP), maximum_font = (FONT[0], 20),
                 steps = 0.2) #Not finished

        #- Stats and stuff ----------------------------------------------------------------------------------------------------------------------------------
        #EquipBox
        dico = {}
        a = ("helmet", "amulet", "armor", "ring", "belt", "weapon", "boots")
        for i in range(len(self.equipment)) :
            if self.equipment[i] != "None" :
                dico[a[i]] = self.equipment[i].picture
            else:
                dico[a[i]] = ICON_PATH + "Equipments/None.png"
            
        EquipBox(main, 8, 4, width = 2, height = 5, icons = dico, icon_path = False)
        
        #HP Max & ATK
        Paragraph(main, 1, 5, width = 3, height = 1, text = "HP" + " " + virgule(str(self.max_HP)) + "\n" + "ATK" + " " + virgule(str(self.max_ATK)), font = (FONT[0], 25))
        #Energy & DEF
        Paragraph(main, 4, 5, width = 4, height = 1, text = "ENG" + " " + virgule(str(self.max_energy)) + "\n" + "DEF" + " " + virgule(str(self.max_DEF)), font = (FONT[0], 25))
        # STR & DEX
        Paragraph(main, 1, 6, width = 3, height = 1, text = "STR" + " " + virgule(str(self.max_STR)) + "\n" + "DEX" + " " + virgule(str(self.max_DEX)), font = (FONT[0], 25))
        # ROB & WIS
        Paragraph(main, 4, 6, width = 4, height = 1, text = "ROB" + " " + virgule(str(self.max_ROB)) + "\n" + "WIS" + " " + virgule(str(self.max_WIS)), font = (FONT[0], 25))
        
        #Elements
        if self.max_res_earth < 0 :
            a = "-"
        else :
            a = ""
        Accentuate(main, 1, 7, width = 3, height = 1, text = "Earth" + " " + a + str(self.max_res_earth) + "%", color = (143, 96, 22, 255))
        
        if self.max_res_water < 0 :
            a = "-"
        else :
            a = ""
        Accentuate(main, 4, 7, width = 4, height = 1, text = "Water" + " " + a + str(self.max_res_water) + "%", color = (96, 201, 255, 255))
        
        if self.max_res_air < 0 :
            a = "-"
        else :
            a = ""
        Accentuate(main, 1, 8, width = 3, height = 1, text = "Air" + " " + a + str(self.max_res_air) + "%", color = (141, 156, 164, 255))
        
        if self.max_res_fire < 0 :
            a = "-"
        else :
            a = ""
        Accentuate(main, 4, 8, width = 4, height = 1, text = "Fire" + " " + a + str(self.max_res_fire) + "%", color = (231, 44, 44, 255))

        #- Social -------------------------------------------------------------------------------------------------------------------------------------------
        #Reputation
        Accentuate(main, 1, 9, width = 6, height = 1, text = "Reputation" + " " + virgule(str(self.reputation)))
        #Bounty
        Accentuate(main, 1, 10, width = 6, height = 1, text = "Bounty" + " " + virgule(str(self.bounty)))
        
        Accentuate(main, 7, 9, width = 4, height = 1, text = "Trophies", justify = "center") #Not finished
        #Trophies
        sub = SubBox(main, 7, 10, minwidth = 3, minheight = 1)
         
        for i in range(len(self.trophies)) :
            ImageBox(sub, i, 0, width = 1, height = 1, image = self.trophies[i].picture)          
            if i == 3:
                break

        image = main.save("mychar")
        await send_temp_image(bot, channel, image)

#-----------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------------------------------------------------#
#                                                                                                           #
#                                     The RPG module and its commands \o/                                   #
#                                                                                                           #
#-----------------------------------------------------------------------------------------------------------#

class Rpg:

    def __init__(self, bot):

        self.bot = bot
        self.masterid = dataIO.load_json("data/red/settings.json")["OWNER"] #list of owners
        self.personnages = dataIO.load_json(PATH + "Characters.json")
        self.banlist = dataIO.load_json(PATH + "banlist.json")
        self.classes =  dataIO.load_json(PATH + "Classes.json")
        self.equipments = dataIO.load_json(PATH + "Equipments.json")



    @commands.command()
    async def rpg_version(self):
        """Show the version of the RPG module
            
           No arguments needed
        """

        await self.bot.say("`Version : " + VERSION + "`")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def rpg_ban(self, ctx, user : discord.Member):
        """Add a member to the blacklist, so he couldn't use the bot anymore

           user : Please mention the Discord user you want to ban
        """

        self.banlist = dataIO.load_json(PATH + "banlist.json") #We load the data
        
        if user.id not in self.banlist:
            
            if user.id not in self.masterid:
                self.banlist.append(user.id)
                dataIO.save_json(PATH + "banlist.json", self.banlist) #We save the data
                await self.bot.say("Done.")
            
            else:
                await self.bot.say("Don't be that funny! :joy:")
        
        else:
            await self.bot.say("Already done.")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def rpg_unban(self, ctx, user : discord.Member):
        """Remove a member from the blacklist, so he could use the bot again \o/

           user : Please mention the Discord user you want to unban
        """

        self.banlist = dataIO.load_json(PATH + "banlist.json") #We load the data

        if user.id in self.banlist:
            self.banlist.remove(user.id)
            dataIO.save_json(PATH + "banlist.json", self.banlist) #We save the data
            await self.bot.say("Done.")
        
        else:
            await self.bot.say("Already done.")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def list_banned(self, ctx):
        """List all the banned members

            No arguments needed
        """

        self.banlist = dataIO.load_json(PATH + "banlist.json") #We load the data

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

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def create_mychar(self, ctx):
        """Starting a new adventure \o/

           No arguments needed
        """
        
        self.personnages = dataIO.load_json(PATH + "Characters.json") #We load the data

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
                    
                    self.classes =  dataIO.load_json(PATH + "Classes.json") #We load the data
                    
                    for i in range(1, len(self.classes) + 1):
                        msg += str(i) + ") " + self.classes[str(i)]["name"] + "\n"

                    msg += "```"
                    await self.bot.say(msg)

                    classchosen = await self.bot.wait_for_message(timeout=60,author=ctx.message.author,channel=ctx.message.channel)
                    
                    if classchosen == None or classchosen.content == "cancel":
                        await self.bot.say("<@" + ctx.message.author.id + ">, the creation of your character has been cancelled! :grimacing:")
                    
                    else:
                        try:
                            classchosen = classchosen.content
                            
                            if int(classchosen) > 0 and int(classchosen) <= len(self.classes):
                                
                                #We save the character in the database
                                self.personnages[ctx.message.author.id] = {}
                                self.personnages[ctx.message.author.id]["name"] = name.content
                                self.personnages[ctx.message.author.id]["HP"] = self.classes[classchosen]["Base HP"]
                                self.personnages[ctx.message.author.id]["DEF"] = self.classes[classchosen]["Base DEF"]
                                self.personnages[ctx.message.author.id]["ATK"] = self.classes[classchosen]["Base ATK"]
                                self.personnages[ctx.message.author.id]["reputation"] = 0
                                self.personnages[ctx.message.author.id]["level"] = 1
                                self.personnages[ctx.message.author.id]["EXP"] = 0
                                self.personnages[ctx.message.author.id]["WonFights"] = 0
                                self.personnages[ctx.message.author.id]["LostFights"] = 0
                                self.personnages[ctx.message.author.id]["bounty"] = 0
                                self.personnages[ctx.message.author.id]["nickname"] = ""
                                self.personnages[ctx.message.author.id]["trophies"] = []
                                self.personnages[ctx.message.author.id]["class"] = classchosen
                                self.personnages[ctx.message.author.id]["CaracPoints"] = 0
                                self.personnages[ctx.message.author.id]["SkillPoints"] = 0
                                self.personnages[ctx.message.author.id]["strength"] = 0
                                self.personnages[ctx.message.author.id]["wisdom"] = 0
                                self.personnages[ctx.message.author.id]["robustness"] = 0
                                self.personnages[ctx.message.author.id]["dexterity"] = 0
                                self.personnages[ctx.message.author.id]["money"] = 0
                                self.personnages[ctx.message.author.id]["skill"] = 100
                                self.personnages[ctx.message.author.id]["energy"] = 6
                                self.personnages[ctx.message.author.id]["guild"] = "None"
                                self.personnages[ctx.message.author.id]["equipment"] = ["None", "None", "None", "None", "None", "None", "None"]
                                self.personnages[ctx.message.author.id]["equipment_invent"] = []
                                self.personnages[ctx.message.author.id]["consumable_invent"] = []
                                self.personnages[ctx.message.author.id]["object_invent"] = []
                                self.personnages[ctx.message.author.id]["creation_date"] = str(ctx.message.timestamp)
                                
                                if len(ctx.message.author.avatar_url) != 0:
                                    
                                    if ctx.message.author.avatar != None:
                                        self.personnages[ctx.message.author.id]["avatar"] = ctx.message.author.avatar_url

                                    else:
                                        self.personnages[ctx.message.author.id]["avatar"] = "DEFAULT AVATAR"
                                
                                else:
                                    self.personnages[ctx.message.author.id]["avatar"] = "None"
                                
                                dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data
                                
                                await self.bot.say("Your character has been successfully created \o/ :")
                                a = Character(ctx.message.author.id)
                                
                                await a.presentation(self.bot, ctx.message.channel)

                            else:
                                await self.bot.say("<@" + ctx.message.author.id + ">, please type a **correct number**!\nThe creation of your character has been cancelled! :grimacing:")
                        
                        except ValueError:
                            await self.bot.say("<@" + ctx.message.author.id + ">, please type a **number**!\nThe creation of your character has been cancelled! :grimacing:")
        
        else:
            await self.bot.say("You already have a character!")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def del_mychar(self, ctx):
        """Delete your character :'(

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            await self.bot.say("Are you sure you want to delete your character?")
            a = Character(ctx.message.author.id)
            await a.presentation(self.bot, ctx.message.channel)
            
            await self.bot.say("If you want to delete your account, just type `yes`!")
            answer = await self.bot.wait_for_message(timeout = 60, author = ctx.message.author, channel = ctx.message.channel)
            
            if answer == None:
                await self.bot.say("I don't wanna wait your answer anymore <@" + ctx.message.author.id + ">! :grimacing:")
            
            else:
                
                if answer.content == "yes":
                    del self.personnages[ctx.message.author.id]

                    dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data

                    await self.bot.say("Your character has been successfully removed! :sob:")
                
                else:
                    await self.bot.say("I guess it's a no ¯\_(ツ)_/¯")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def mychar (self, ctx):
        """Show your character stats

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await a.presentation(self.bot, ctx.message.channel)

#-----------------------------------------------------------------------------------------------------------#
    
    @commands.command(pass_context=True)
    async def rename_mychar(self, ctx, *name):
        """Rename your character

           name : The new name for your character!
        """
        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            name = " ".join(name)
            
            if len(name) > 19:
                await self.bot.say("<@" + ctx.message.author.id + ">, please take a name with less than 20 characters! :grimacing:")
            
            else:
                self.personnages[ctx.message.author.id]["name"] = name

                dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data

                await self.bot.say("Your character's name has been successfully changed!")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def avatar_mychar(self, ctx, link : str = ""):
        """Set an avatar for your character

           link : The link to the new picture for your character! It must be a correct picture link, take care my child
        """
        
        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            if link == "":
                link = ctx.message.author.avatar_url
            await self.bot.say(a.set_avatar(link))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def attrib(self, ctx):
        """To set your caracteristic points

            No arguments needed
        """
        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await a.attrib_cpts(self.bot, ctx.message.author, ctx.message.channel)

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def inventory(self, ctx):
        """Show your inventory through a private message

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await self.bot.send_message(ctx.message.author, a.inventory.show_inventory())

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def equipment(self, ctx):
        """Show your inventory throuhgh a private message

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await self.bot.send_message(ctx.message.author, a.show_equipment())

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def equip(self, ctx):
        """To change your equipment

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await a.equip(self.bot, ctx.message.author)

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    async def unequip(self, ctx):
        """To unequip an item

           No arguments needed
        """

        if (await check_have_character(self.bot, ctx.message.channel, ctx.message.author)):
            a = Character(ctx.message.author.id)
            await a.unequip(self.bot, ctx.message.author)

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def give_object(self, ctx, user : discord.Member, item : str, nb : int = 1):
        """Give an amount of an item to a member

           user : The Discord member you want to give an amount of a specified object
           item : The ID of the object you want to give
           nb   : The amount of this object you want to give (DEFAULT VALUE = 1)
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            a = Character(user.id)
            await self.bot.say(a.give_object(item,nb))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def remove_object(self, ctx, user : discord.Member, item : str, nb : int = -1):
        """Remove an amount of an object from a member's inventory

           user : The Discord member you want to remove an amount of a specified object
           item : The ID of the object you want to remove
           nb   : The amount of this object you want to remove (DEFAULT VALUE = -1 --> Remove totally this object from the member's inventory)
        """

        self.personnages = dataIO.load_json(PATH + "Characters.json") #We load the data

        if user.id in self.personnages:
            a = Character(user.id)
            await self.bot.say(a.remove_object(item,nb))
        
        else:
            await self.bot.say(user.name + NO_CHAR_MSG)

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def give_consumable(self, ctx, user : discord.Member, item : str, nb : int = 1):
        """Give an amount of an equipment to a member

           user : The Discord member you want to give an amount of a specified equipment
           item : The ID of the equipment you want to give
           nb   : The amount of this equipment you want to give (DEFAULT VALUE = 1)
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            a = Character(user.id)
            await self.bot.say(a.give_consumable(item,nb))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def remove_consumable(self, ctx, user : discord.Member, item : str, nb : int = -1):
        """Remove an amount of a consumable from a member's inventory

           user : The Discord member you want to remove an amount of a specified consumable
           item : The ID of the consumable you want to remove
           nb   : The amount of this consumable you want to remove (DEFAULT VALUE = -1 --> Remove totally this consumable from the member's inventory)
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            a = Character(user.id)
            await self.bot.say(a.remove_consumable(item,nb))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def give_equip(self, ctx, user : discord.Member, itemID : str, nb : int = 1):
        """Give an amount of a consumable to a member

           user : The Discord member you want to give an amount of a specified consumable
           item : The ID of the consumable you want to give
           nb   : The amount of this consumable you want to give (DEFAULT VALUE = 1)
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            a = Character(user.id)
            await self.bot.say(a.give_equip(itemID,nb))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def remove_equip (self, ctx, user : discord.Member, itemID : str, nb : int = -1):
        """Remove an amount of an equipment from a member's inventory

           user : The Discord member you want to remove an amount of a specified equipment
           item : The ID of the equipment you want to remove
           nb   : The amount of this equipment you want to remove (DEFAULT VALUE = -1 --> Remove totally this equipment from the member's inventory)
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            a = Character(user.id)
            await self.bot.say(a.remove_equip(itemID,nb))

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def set_char(self, ctx, user : discord.Member, carac : str, *value):
        """Set a caracteristic to a value for a specified member

           user  : The Discord member you want to change a caracteristic value
           carac : The concerned caracteristic name
           value : The new value you want to set to this caracteristic 
        """

        #This command is a bit messy and it would be interesting to improve her. Since, we can directly edit the database, it's not that important tho

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            
            if carac in self.personnages[user.id]:
                value = " ".join(value)
                
                if str(type(self.personnages[user.id][carac])) == "<class 'int'>": #int value waited
                    try:
                        value = int(value)
                        self.personnages[user.id][carac] = value

                        dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data

                        await self.bot.say("The caracteristic has been successfully updated!")
                    
                    except ValueError:
                        await self.bot.say("The format of the caracteristic isn't correct! :grimacing:")
                
                elif str(type(self.personnages[user.id][carac])) == "<class 'list'>": #list value waited

                    #This part would be interesting to improve so we could set multidimensionnal lists
                    
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

                    dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data

                    await self.bot.say("The caracteristic has been successfully updated!")
                
                elif str(type(self.personnages[user.id][carac])) == "<class 'str'>":

                    self.personnages[user.id][carac] = value

                    dataIO.save_json(PATH + "Characters.json", self.personnages) #We save the data

                    await self.bot.say("The caracteristic has been successfully updated!")
                
                else:
                    await self.bot.say("The format of the caracteristic isn't correct! :grimacing:")
            
            else:
                await self.bot.say("Please type a correct caracteristic name! :grimacing:")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def show_char(self, ctx, user : discord.Member, carac : str):
        """Show a caracteristic of a member's character

           user  : The Discord member you want to check a caracteristic
           carac : The caracteristic name you want to check
        """

        if (await check_have_character(self.bot, ctx.message.channel, user)):
            
            if carac in self.personnages[user.id]:
                await self.bot.say("Here's what you requested : `" + str(self.personnages[user.id][carac]) + "`")
            
            else:
                await self.bot.say("Please type a correct caracteristic name! :grimacing:")

#-----------------------------------------------------------------------------------------------------------#

    @commands.command()
    async def infos_equip(self, *name):
        """Get infos from a specified equipment

           name : The name of the equipment you want to get infos from
        """

        self.equipments = dataIO.load_json(PATH + "Equipments.json") #We load the data
        
        name = " ".join(name)
        
        if name != "":
            name = name.lower()
            equip = None
            
            for objet in self.equipments:
                if self.equipments[objet]["name"].lower() == name:
                    equip = Equipment(objet)
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

#-----------------------------------------------------------------------------------------------------------#

    @commands.command()
    async def infos_class(self, name : str = ""):
        """Get infos from a specified classe or for all the existing ones

           name : The name of the class you want to get infos from
        """

        self.classes =  dataIO.load_json(PATH + "Classes.json") #We load the data
        
        res = "-2"
        if name != "":
            name = name[0].upper() + name[1:]
            res = "-1"
            for classe in self.classes:
                if self.classes[classe]["name"] == name:
                    res = classe
                    break

        if res == "-1":
            await self.bot.say("Please type a **correct** class name! :grimacing:")
        
        else:
            msg = "```Markdown\n"
                
            if name == "":
                for classe in self.classes:
                    a = Classe(classe)
                    msg += a.presentation()
                
            else:
                a = Classe(res)
                msg += a.presentation()
                
            msg += "```"
                
            await self.bot.say(msg)

#-----------------------------------------------------------------------------------------------------------#


def setup(bot):
    bot.add_cog(Rpg(bot))
