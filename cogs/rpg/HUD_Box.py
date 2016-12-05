#V2.0
#A bunch of classes.
#MasterBox is the main class ; you must create one each time you want to display something.

#For example :
#   name = "Demo"
#   box = MasterBox(...) ##Creating the masterbox
#   ImageBox(box, ...) ##Creating an image on the masterbox
#   ... ##Other boxes here (TextBox, BodyBox, whatever box). The first argument is always the BoxMaster. No need to keep them in variables ; you can consider them as procedures. See below why they are objects and not procedures.
#   image = box.save(name) ##box.save() returns a string which is the path of the saved image (builded with 'name' argument)

#This module can handle situations where a box is greater than expected (for text mainly). However don't count on this feature, the result if often ugly.
#Be as careful as possible with elements size.


#To do :

# - Redo offset algorithm.
# - AvatarBox / GaugeBox : shaders ?
# - GaugeBox : when the percentage is 0%, two pixels are on the border.
# - AvatarBox : background is not displayed in circle mode ('im' transparency erases 'back' color)


#- Current boxes ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#In order :

# MasterBox
# SubBox
# TextBox
#   Styles (different sets of default parameters) :
#       Title(master, X, Y, width, height, text)
#       Subtitle(same arguments)
#       Paragraph(same)
#       Accentuate(same)
# ImageBox
# EquipBox
# AvatarBox (square and circle)
# GaugeBox


#- Useful functions -------------------------------------------------------------------------------------------------------------------------------------------------------------------

# percent_color : considering a scale where extrema are associated with colors and value within this scale, returns color associated with value.
# percent : returns the percentage of a value considering a scale. Though this is not a real percentage, but a float between 0 and 1 (a percentage divided by 100).
# color_to_string : put a color into a string format (with alpha and without '#'). Useful to stock colors in data base.
# string_to_color : take a string formated color and convert it into a tuple, to be used by this module.
# float_range : a range-like function but works also with floats.



from PIL import Image, ImageDraw, ImageFont

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Declarations of constants
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

HUD_VERSION = "1.2.0"

SQUARE = 48
SUBSQUARE = int(SQUARE/2)

HUD_PATH = "data/rpg/Images/HUD/"
ICON_PATH = "data/rpg/Images/Icons/"
FONT_PATH = "data/rpg/"
TEMP_PATH = "data/rpg/temp/"
FONT = ('Barthowheel Regular.ttf', 24) #Add .ttf at the end of first element if the font is stored in game directories.

EQUIP_COLORS = {(0, 0, 255, 255) : "helmet", (255, 0, 0, 255) : "amulet", (255, 255, 0, 255) : "armor", (255, 0, 255, 255) : "belt",
                (0, 255, 0, 255) : "ring", (0, 255, 255, 255) : "weapon", (255, 255, 255, 255) : "boots"}
BACKGROUND_COLOR = (190, 144, 78, 255)
BACKGROUND_COLOR2 = (150, 102, 34, 255)
BORDER_COLOR = (120, 78, 19, 255)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Exceptions
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class StringArgumentError(Exception) :
    """Raised when overflow argument (for some boxes) is not handled, or shape for AvatarBox."""
    def __init__(self, wrongArg : str) :
        Exception.__init__(self, "incorrect argument '" + str(wrongArg) + "'")

class BoxSizeError(Exception) :
    """Raised when size arguments are not big enough, that is inferior to 1"""
    def __init__(self, wrongSize) :
        Exception.__init__(self, "incorrect argument '" + str(wrongSize) + "'")

class BoxIndexError(Exception) :
    """Raised when you're trying to put a box outside its master."""
    def __init__(self, wrongIndex, masterSize : int) :
        Exception.__init__(self, "incorrect argument '" + str(wrongIndex) + "'. Master size : '" + str(masterSize) + "'")

class OverlayedBoxesError(Exception) :
    """Raised when two boxes with the same class have the same coordinates."""
    def __init__(self, wrongID) :
        Exception.__init__(self, "two boxes with same ID : ( " + str(wrongID[0]) + "," + str(wrongID[0]) + "," + wrongID[2] + ")")

class EquipBoxError(Exception) :
    """All errors specific to EquipBox, as no matching dictionnaries, or asked colors not found."""
    def __init__(self, string) :
        Exception.__init__(self, string)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   Functions
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def percent_color(maximum_color : tuple, maximum : float, minimum_color : tuple, minimum : float, current : float) :

    """Returns a color tuple corresponding to 'current' when maximum_color and minimum_color are corresponding to maximum and minimum.
    maximum_color : color corresponding to maximum.
    maximum : 100% (maximum isn't a percentage though).
    minimum_color : color corresponding to minimum.
    minimum : 0%
    current : a value between minimum and maximum."""


    coef = percent(1, minimum / maximum, current / maximum)
    current_color = [0,0,0,0]
    for i in range(4) :
        current_color[i] = int( reci_percent(maximum_color[i], minimum_color[i], coef) )
        
    return tuple(current_color)


def percent(maximum : float, minimum : float, current : float, limit : bool = True) :

    """With maximum at 100% and minimum at 0%, computes the percentage of current."""

    if maximum - minimum == 0 :
        return 1.0
        #raise ZeroDivisionError("percent : maximum and minimum cannot be equal")

    if limit and current > maximum :
        current = maximum
    elif limit and current < minimum :
        current = minimum

    return (current - minimum) / (maximum - minimum)


def reci_percent(maximum : float, minimum : float, percentage : float) :

    """With maximum at 100% and minimum at 0%, computes the value corresponding to percentage."""

    if maximum - minimum == 0 :
        return maximum
        #raise ZeroDivisionError("reci_percent : maximum and minimum cannot be equal")


    return ( percentage * (maximum - minimum) ) + minimum
    

def color_to_string(color) :
    
    result = ""
    for i in color :
        result += format(i, "02x")

    return  result


def string_to_color(string) :

    color = []
    for i in range( 0, len(string), 2) :
        color.append( int( string[i:i+2], 16) )

    return tuple(color)


def float_range(start, end, steps, include = False) :
    
    suit = []
    if not(include) :
        start += steps
    while start < end :
        suit.append(start)
        start += steps

    return tuple(suit)


def polygon( rectangle ) :
    """rectangle is 2 2-tuple within a 2-tuple."""

    d = int( (rectangle[1][1] - rectangle[0][1]) / 3) 
    if rectangle[1][0] - rectangle[0][0] < 2*d :
        d = 0
    

    return ( (rectangle[0][0], rectangle[0][1] + d),
             (rectangle[0][0] + d, rectangle[0][1]),
             
             (rectangle[1][0] - d, rectangle[0][1]),
             (rectangle[1][0], rectangle[0][1] + d),
             
             (rectangle[1][0], rectangle[1][1] - d),
             (rectangle[1][0] - d, rectangle[1][1]),

             (rectangle[0][0] + d, rectangle[1][1]),
             (rectangle[0][0], rectangle[1][1] - d)
             )


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   MasterBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class MasterBox(object) :

    """Main class. Call it each time you want to use this module."""

    def __init__(self, minwidth : int, minheight : int, appearance : str = "HUD_Box_Parchemin V4.png", show : bool = True, overflow : str = "bottom") :

        """Doesn't create any image. See get() method.
        minwidth, minlength : units : case (48*48 pixels)
        appearance : path of background image
        show : if True, show background
        overflow : "bottom" or "right". If bottom : wrap textsBox and make MasterBox bigger (length +) if necessary (and adapt positions of the other boxes)
                                        If right : no wrapping. Make MasterBox bigger (width +) if necessary, adapt positions of the other boxes.
                    No other values ! (exception WrongOverflow)
        """

        if overflow not in ("right", "bottom") :
            raise StringArgumentError(overflow)
        if minheight < 1 :
            raise BoxSizeError(minheight)
        if minwidth < 1 :
            raise BoxSizeError(minwidth)

        
        
        self.width = minwidth
        self.height = minheight
        self.appearance = HUD_PATH + appearance #I can make a condition with self.show, but it's almost useless.
        self.overflow = overflow
        self.show = show

        self.minwidth = minwidth
        self.minheight = minheight
        self.expected_size = (minwidth, minheight)
        self.offsetH = 0
        self.offsetV = 0

        self.boxes = {}
        if type(self) != SubBox :
            self.memorizer = {"fonts" : {}, "boxes" : {}}

        


    def add_box(self, box) :

        if ( box.X, box.Y, str(type(box)) ) in self.boxes.keys() :
            raise OverlayedBoxesError( ( box.X, box.Y, str(type(box)) ) )
        
        self.boxes[( box.X, box.Y, str(type(box)) )] = box


    def get_image(self) :
        
        if self.show :

            if self.appearance not in self.memorizer["boxes"].keys() :

                #Cutting image
                sourceImage = Image.open(self.appearance)
                self.memorizer["boxes"][self.appearance] = {}


                #------------------------------------------------------------------------------------------------------
                #Corners
                self.memorizer["boxes"][self.appearance]["corners"] = {}
                useless = range(2)
                for i in useless :
                    for j in useless :

                        for k in useless :
                            for l in useless :
                            
                                X = i * SQUARE * 2 + k * SUBSQUARE
                                Y = j * SQUARE * 2 + l * SUBSQUARE
                                self.memorizer["boxes"][self.appearance]["corners"][ (2*i+k, 2*j+l) ] = sourceImage.crop( (X, Y, X+SUBSQUARE, Y+SUBSQUARE) )

                #------------------------------------------------------------------------------------------------------
                #Hborders (left and right)
                self.memorizer["boxes"][self.appearance]["Hborders"] = {}

                Y = SQUARE
                for i in useless :
                    for j in useless :

                        X = i * SQUARE * 2 + j * SUBSQUARE
                        self.memorizer["boxes"][self.appearance]["Hborders"][ 2*i+j ] = sourceImage.crop( (X, Y, X+SUBSQUARE, Y+SQUARE) )

                #------------------------------------------------------------------------------------------------------
                #Vborders (top and bottom)
                self.memorizer["boxes"][self.appearance]["Vborders"] = {}

                X = SQUARE
                for i in useless :
                    for j in useless :

                        Y = i * SQUARE * 2 + j * SUBSQUARE
                        self.memorizer["boxes"][self.appearance]["Vborders"][ 2*i+j ] = sourceImage.crop( (X, Y, X+SQUARE, Y+SUBSQUARE) )
          
                #------------------------------------------------------------------------------------------------------
                #Big center square
                self.memorizer["boxes"][self.appearance]["middle"] = sourceImage.crop( (1*SQUARE, 1*SQUARE, 2*SQUARE, 2*SQUARE) )




            #------------------------------------------------------------------------------------------------------
            #Putting images to create a whole box
            totalWidth = self.width * SQUARE
            totalHeight = self.height * SQUARE
            image = Image.new("RGBA", (totalWidth, totalHeight), (0,0,0))
            
            #Subsquare corners
            image.paste(self.memorizer["boxes"][self.appearance]["corners"][(0,0)], (0, 0) )
            image.paste(self.memorizer["boxes"][self.appearance]["corners"][(3,0)], (totalWidth - SUBSQUARE, 0) )
            image.paste(self.memorizer["boxes"][self.appearance]["corners"][(0,3)], (0, totalHeight - SUBSQUARE) )
            image.paste(self.memorizer["boxes"][self.appearance]["corners"][(3,3)], (totalWidth - SUBSQUARE, totalHeight - SUBSQUARE) )



            #Rest of corners and borders (top and bottom)
            wideEnough = (totalWidth > SQUARE)            
            if wideEnough :

                #top
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(1,0)], (SUBSQUARE, 0))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(2,0)], (totalWidth - 2*SUBSQUARE, 0))

                for i in range(1, int(totalWidth/SQUARE) - 1) : #Middle top cases, top half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Vborders"][0], (i*SQUARE, 0))

                #bottom
                useless = totalHeight - SUBSQUARE
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(1,3)], (SUBSQUARE, useless))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(2,3)], (totalWidth - 2*SUBSQUARE, useless))

                for i in range(1, int(totalWidth/SQUARE) - 1) : #Middle bottom cases, bottom half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Vborders"][3], (i*SQUARE, useless))



            #Rest of corners and borders (left and right)
            highEnough = (totalHeight > SQUARE)            
            if highEnough :

                #left
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(0,1)], (0, SUBSQUARE))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(0,2)], (0, totalHeight - 2*SUBSQUARE))

                for i in range(1, int(totalHeight/SQUARE) - 1) : #Middle left cases, left half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Hborders"][0], (0, i*SQUARE))

                #right
                useless = totalWidth - SUBSQUARE
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(3,1)], (useless, SUBSQUARE))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(3,2)], (useless, totalHeight - 2*SUBSQUARE))

                for i in range(1, int(totalHeight/SQUARE) - 1) : #Middle right cases, right half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Hborders"][3], (useless, i*SQUARE))


            if wideEnough and highEnough :

                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(1,1)], (SUBSQUARE, SUBSQUARE))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(2,1)], (totalWidth - 2*SUBSQUARE, SUBSQUARE))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(1,2)], (SUBSQUARE, totalHeight - 2*SUBSQUARE))
                image.paste(self.memorizer["boxes"][self.appearance]["corners"][(2,2)], (totalWidth - 2*SUBSQUARE, totalHeight - 2*SUBSQUARE))


                for i in range(1, int(totalWidth/SQUARE) - 1) : #Middle top cases, bottom half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Vborders"][1], (i*SQUARE, SUBSQUARE))

                useless = totalHeight - 2*SUBSQUARE
                for i in range(1, int(totalWidth/SQUARE) - 1) : #Middle bottom cases, top half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Vborders"][2], (i*SQUARE, useless))

                for i in range(1, int(totalHeight/SQUARE) - 1) : #Middle left cases, right half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Hborders"][1], (SUBSQUARE, i*SQUARE))

                useless = totalWidth - 2*SUBSQUARE
                for i in range(1, int(totalHeight/SQUARE) - 1) : #Middle right cases, left half                    
                    image.paste(self.memorizer["boxes"][self.appearance]["Hborders"][2], (useless, i*SQUARE))


                if totalWidth > 2*SQUARE and totalHeight > 2*SQUARE :

                    for i in range(1, int(totalWidth/SQUARE) - 1) : #Middle
                        for j in range(1, int(totalHeight/SQUARE) - 1) :
                            image.paste(self.memorizer["boxes"][self.appearance]["middle"], (i*SQUARE, j*SQUARE) )

                           
        else :
            image = None


        return image



    def get_box(self) :
        
        result = Image.new("RGBA", (SQUARE, SQUARE), (0,0,0,0))
        
        for i in sorted(self.boxes.keys()) :

            expected = self.boxes[i].expected_size
            
            if type(self.boxes[i]) == SubBox :
                image = self.boxes[i].get_box()
            else :
                image = self.boxes[i].get_image()

            if image != None :


                #Adapts width
                useless = image.size[0] + (i[0] + self.offsetH) * SQUARE
                if result.size[0] < useless :

                    newsize = result.size[0]
                    while newsize < useless :
                        newsize += SQUARE
                        
                    result = result.crop( (0, 0, newsize, result.size[1]) )

                #Adapts height
                useless = image.size[1] + (i[1] + self.offsetV) * SQUARE
                if result.size[1] < useless :

                    newsize = result.size[1]
                    while newsize < useless :
                        newsize += SQUARE
                        
                    result = result.crop( (0, 0, result.size[0], newsize) )
                
                #Pastes image on result
                result.paste( image, ((i[0] + self.offsetH) * SQUARE, (i[1] + self.offsetV) * SQUARE), image )

                #Computes offsets (for other boxes)
                got = (int(image.size[0] / SQUARE), int(image.size[1] / SQUARE) )
                if expected[0] <= got[0] :
                    self.offsetH += int(got[0] - expected[0])
                if expected[1] <= got[1] :
                    self.offsetV += int(got[1] - expected[1])

        
        useless = result.size[0]/SQUARE
        while self.width < useless :
            self.width += 1
        useless = result.size[1]/SQUARE
        while self.height < useless :
            self.height += 1
            
        image = self.get_image()
        if image == None :
            image = Image.new("RGBA", (self.width*SQUARE, self.height*SQUARE), (0,0,0,0))

                        
        image.paste(result, (0,0), result)
            
        return image



    def save(self, name : str) :

        im = self.get_box()
        filename = TEMP_PATH + name + ".png"
        im.save(filename, "PNG")

        return filename
                

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   SubBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------        

class SubBox(MasterBox) :

    """Actually a MasterBox with Master. Useful if you want several boxes in one image : put False to 'show' for the masterBox, and True for the subboxes."""

    def __init__(self, master : MasterBox, X : int, Y : int, minwidth, minheight, appearance = "HUD_Box_Parchemin V4.png", show = True, overflow = "bottom") :

        """master : the master box, or another box.
        X and Y : entire coordinates of box' top-left corner (units : cases)
        See MasterBox for other arguments."""
        
        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if X + minwidth > master.width :  #Raises BoxSizeErrors only at the declaration. For added TextBox for example, adapt the size of masters.
            raise BoxSizeError("X + minwidth")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if Y + minheight > master.height :
            raise BoxSizeError("Y + minheight")
        

        self.master = master
        self.X = X
        self.Y = Y
        self.memorizer = master.memorizer
        MasterBox.__init__(self, minwidth, minheight, appearance, show, overflow)

        self.master.add_box(self)
            
            
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   TextBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class TextBox(object) :

    """Obviously allows to display text in boxes. To wrap it (or not) : see attribute "overflow" (MasterBox and SubBox)
    master : the master box, or another box.
    X and Y : entire coordinates of text's top-left corner (units : case)
    width and height : similar to minwidth and minheight from MasterBox classes. Allow to create spaces which can be taken by text without moving boxes.
    text : I guess you can guess.
    font : a tuple containing font name (in a string), and its size in pixels. See FONT constant.
    color : a 4-tuple containing pixel information (last rank is for alpha)
    lines_per_square : an integer representing how many lines can be putted on a square (in height, not width). If font[1] is too big, it is resized to match with lines_per_square.
    first_line : the number of the line where text's first line will be printed. This is an index, so begin with 0. If too big, take lines_per_squares-1 (its maximum value).
    justify : can be "right", "left" or "center".
    margin : the space, in pixels, between text and its horizontal border (for an equivalent for height, see first_line).
    """

    def __init__(self, master : MasterBox, X : int, Y : int, width : int, height : int, text : str, font : tuple = FONT, color : str = (0,0,0,255),
                 lines_per_square : int = 2, first_line : int = 0, justify : str = "center", margin : int = int(SUBSQUARE/2)) :

        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if X + width > master.width :
            raise BoxSizeError("X + width")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if Y + height > master.height :
            raise BoxSizeError("Y + height")

        if width < 1 :
            raise BoxSizeError("width < 1")
        if height < 1 :
            raise BoxSizeError("height < 1")

        if justify not in ("left", "center", "right") :
            raise StringArgumentError(justify)

        if first_line >= lines_per_square :
            first_line = lines_per_square - 1
        elif first_line < 0 :
            first_line = 0

        self.master = master
        self.X, self.Y = X, Y
        self.width = width*SQUARE - 2*margin
        self.height = height*SQUARE - SUBSQUARE
        self.expected_size = (width, height)
        self.text = text
        self.color = color
        
        self.line_height = int(SQUARE / lines_per_square)
        self.first_line = first_line
        self.justify = justify
        self.margin = margin

        if font[1] > self.line_height :
            font = (font[0], self.line_height)
        self.font = font

        master.add_box(self)


    def get_image(self) :
        
        im = ImageDraw.Draw(Image.new("RGBA", (SQUARE, SQUARE), (0,0,0,0)))

        if self.font not in self.master.memorizer["fonts"].keys() :
            self.master.memorizer["fonts"][self.font] = ImageFont.truetype(FONT_PATH + self.font[0], self.font[1])

        possible = len(self.text) > 0
        while possible and self.text[-1] == " " :
            self.text = self.text[:-1]
            possible = len(self.text) > 0
        
        actualWidth = im.textsize(self.text, font = self.master.memorizer["fonts"][self.font])[0]

        if self.master.overflow == "bottom" and possible and actualWidth > self.width : #Wrap the text

            if self.text[0] != " " :
                self.text = " " + self.text
            
            spaces = [] #Uses spaces as possible separations between lines.
            for i in range(len(self.text)) :
                if self.text[i] == " " :
                    spaces.append(i)

            maxi = (0, 0)
            maxLength = 0
            for i in range(len(spaces) - 1) :
                useless = im.textsize(self.text[spaces[i]+1:spaces[i+1]], font = self.master.memorizer["fonts"][self.font])[0]
                if maxLength < useless :
                    maxLength = useless
                    maxi = (i, i+1)

            if maxi[0] != maxi[1] :
                useless = im.textsize(self.text[ spaces[maxi[0]]+1 : spaces[maxi[1]] ], font = self.master.memorizer["fonts"][self.font])[0]
                while useless > self.width :
                    self.width += SQUARE
            #Now we are sure there is at least one way to wrap self.text with the desired length...


            while actualWidth > self.width : #So we can do this

                inf = 0
                sup = 0
                possible = sup < len(spaces)
                while possible and im.textsize(self.text[ spaces[inf]+1 : spaces[sup] ], font = self.master.memorizer["fonts"][self.font])[0] < self.width :
                    sup += 1
                    possible = sup < len(spaces)
                sup -= 1
                self.text = self.text[ :spaces[sup]] + "\n" + self.text[spaces[sup] + 1:]                    
                inf = sup
                actualWidth = im.textsize(self.text, font = self.master.memorizer["fonts"][self.font])[0]

            while self.text[0] == " " :
                self.text = self.text[1:]

        lines = self.text.split("\n")
        
            
        height = self.line_height * (len(lines) + self.first_line)
        Y = 0
        while Y < height :
            Y += SQUARE


        im = Image.new("RGBA", ( actualWidth + 2*self.margin, Y), (0,0,0,0))
        result = ImageDraw.Draw(im)
        
        middle = int( (self.line_height - self.font[1]) /2)
        if self.justify == "left" :
            for i in range(len(lines)) :
                result.text( (self.margin, self.line_height * (i + self.first_line) + middle),
                             lines[i], font = self.master.memorizer["fonts"][self.font], fill = self.color)
                
        elif self.justify == "right" :
            for i in range(len(lines)) :
                result.text( ( im.size[0] - result.textsize(lines[i], self.master.memorizer["fonts"][self.font])[0],
                               self.line_height * (i + self.first_line) + middle),
                             lines[i], font = self.master.memorizer["fonts"][self.font], fill = self.color)

        else : #center
            for i in range(len(lines)) :
                result.text( ( int((im.size[0] - result.textsize(lines[i], self.master.memorizer["fonts"][self.font])[0] + 2*self.margin) / 2),
                               self.line_height * (i + self.first_line) + middle),
                             lines[i], font = self.master.memorizer["fonts"][self.font], fill = self.color)

        
        result = ImageDraw.Draw(im)
        actualWidth = im.getbbox()
        if actualWidth == None :
            im = None
        else :
            im = im.crop( (0, 0, actualWidth[2], actualWidth[3]) )

                        
        return im




#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   ImageBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class ImageBox(object) :


    """Allows to display images. The image will be centered in the area (X, Y, X + width, Y + height).
    master : the master box, or another box.
    X and Y : entire coordinates of text's top-left corner (units : case)
    width and height : same as TextBox, but can't be overflowed except if size is not given. (units : case)
    image : file path.
    resize : if True, the image will be resized.
    size : a 2-tuple containing the width and the length after resizing.
    icon : if True, add automatically ICON_PATH to file path. Don't forget this parameter when you're not displaying an image.
    frame : if True, will display a box under image.
    frame_appearance : (useless when frame is False) Box' image path."""

    def __init__(self, master,  X : int, Y : int, width : int, height : int, image : str, resize : bool = False, size : tuple = (SUBSQUARE, SUBSQUARE),
                 icon : bool = True, frame : bool = False, frame_appearance : str = "HUD_Box_Parchemin V4.png") :

    
        if len(size) != 2 or int(size[0]/SQUARE) > width or int(size[1]/SQUARE) > height :
            raise BoxSizeError("wrong size argument : " + str(size))
        
        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if X + width > master.width :
            raise BoxSizeError("X + width")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if Y + height > master.height :
            raise BoxSizeError("Y + height") 

        self.master = master

        self.X = X
        self.Y = Y
        self.width = width * SQUARE
        self.height = height * SQUARE
        self.expected_size = (width, height)

        if icon :
            self.image = ICON_PATH + image
        else :
            self.image = image
        self.resize = resize
        if self.resize :
            self.size = size

        self.icon = icon
        self.frame = frame
        if frame :
            self.frame_appearance = frame_appearance

        master.add_box(self)


    def get_image(self) :

        im = Image.open(self.image)
        
        if self.resize :
            im = im.resize(self.size)
        else :

            while im.size[0] > self.width :
                self.width += SQUARE
            while im.size[1] > self.height :
                self.height += SQUARE

        result = Image.new("RGBA", (self.width, self.height), (0,0,0,0))

        if self.frame :
            temp = MasterBox(int(self.width/SQUARE), int(self.height/SQUARE), self.frame_appearance) #Can't use self.master because it would perturb image creation.
            temp.memorizer = self.master.memorizer
            box = temp.get_image()
            del temp

            result.paste(box, (0, 0))

        result.paste(im, (int( (self.width - im.size[0]) / 2), int( (self.height - im.size[1]) / 2)), im )
        
        return result


class Title(TextBox) :
    def __init__(self, master, X, Y, width, height, text, font = (FONT[0], 40), color = (0,0,0,255),
                 lines_per_square = 1, first_line = 0, justify = "center", margin = int(SUBSQUARE/2)) :
        TextBox.__init__(self, master, X, Y, width, height, text, font, color, lines_per_square, first_line, justify, margin)

class Subtitle(TextBox) :
    def __init__(self, master, X, Y, width, height, text, font = (FONT[0], 30), color = (0,0,0,255),
                 lines_per_square = 1, first_line = 0, justify = "center", margin = SUBSQUARE) :
        TextBox.__init__(self, master, X, Y, width, height, text, font, color, lines_per_square, first_line, justify, margin)

class Paragraph(TextBox) :
    def __init__(self, master, X, Y, width, height, text, font = (FONT[0], 20), color = (0,0,0,255),
                 lines_per_square = 2, first_line = 0, justify = "left", margin = int(SUBSQUARE/2)) :
        TextBox.__init__(self, master, X, Y, width, height, text, font, color, lines_per_square, first_line, justify, margin)

class Accentuate(TextBox) :
    def __init__(self, master, X, Y, width, height, text, font = (FONT[0], 24), color = (0,0,0,255),
                 lines_per_square = 1, first_line = 0, justify = "left", margin = int(SUBSQUARE/2)) :
        TextBox.__init__(self, master, X, Y, width, height, text, font, color, lines_per_square, first_line, justify, margin)


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   EquipBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class EquipBox(object) :

    """Replace squares by icons. Squares are identified by unique color at their upper-left corner.
    master : always the same story.
    X and Y : same.
    width and height : same.
    icons : a dictionnary containing paths to icon image files. Be sure all keys in icons are also in colors' values.
    colors : a dictionnary containing 4-tuple (r, g, b, alpha). Shows what colors EquipBox has to find. Colors and icons are related via keys.
    image : path to EquipBox image (which contains colored squares).
    square_size : a 2-tuple containing the width and height of a square. Resize images when too big.
    background_color : the color to put beyond icons, to hide colored squares. A 4-tuple (r, g, b, alpha) (from 0 to 255). Put 0 to alpha if you don't want background color.
    icon_path : if True, add ICON_PATH to each file path in icons.
    """

    def __init__(self, master : MasterBox, X : int, Y : int, width : int, height : int, icons : dict, colors : dict = EQUIP_COLORS, image : str = "Human.png",
                 square_size : tuple = (SUBSQUARE, SUBSQUARE), background_color : tuple = BACKGROUND_COLOR, icon_path : bool = True) :

        
        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if X + width > master.width :
            raise BoxSizeError("X + width")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if Y + height > master.height :
            raise BoxSizeError("Y + height")

        if sorted(icons.keys()) != sorted(colors.values()) :
            raise EquipBoxError("no matching dictionnaries' keys : icons attribute must have colors attribute's values as keys.")

        self.master = master
        
        self.X, self.Y = X, Y
        self.width, self.height = width * SQUARE, height * SQUARE
        self.expected_size = (width, height)

        self.icons = icons
        self.colors = colors

        self.image = HUD_PATH + image
        self.square_size = square_size
        self.background_color = background_color
        if icon_path :
            for i in self.icons.keys() :
                self.icons[i] = ICON_PATH + self.icons[i]

        master.add_box(self)


    def get_image(self) :

        im = Image.open(self.image)
        array = im.load()

        spots = {}
        allFound = len(spots) == len(self.icons)
        i = 0


        rainbow = self.colors.keys()
        
        while not(allFound) and i < im.size[0] :
            j = 0
            while not(allFound) and j < im.size[1] :
                if array[i, j] in rainbow :
                    spots[ (i, j) ] = self.icons[self.colors[array[i, j]]]
                    #Should be optimized (block assignation when already found)
                allFound = len(spots) == len(self.icons)
                j += 1
            i += 1

        if not(allFound) :
            raise EquipBoxError("missing color(s) : " + str(self.icons))

        square = Image.new("RGBA", self.square_size, self.background_color)
        for i in spots.keys() :
            im.paste(square, i, square)
            icon = Image.open(spots[i])
            if icon.size[0] > self.square_size[0] or icon.size[1] > self.square_size[1] :
                icon = icon.resize(self.square_size)
            im.paste(icon, i, icon)

        X, Y = 0, 0
        while im.size[0] > X :
            X += SQUARE
        while im.size[1] > Y :
            Y += SQUARE

        result = Image.new( "RGBA", (X,Y), (0,0,0,0) )
        result.paste(im, ( int( (X - im.size[0]) / 2), int( (Y - im.size[1]) / 2) ), im)
        
        
        return result


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   AvatarBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class AvatarBox(object) :

    """An image bordered by a squared or circled gauge (one border represents 25% when the gauge is squared).
    master, X, Y, width, height : you know, I guess.
    image : path to image file (not gauge)
    maximum : 100% (maximum is not a percentage though)
    minimum : 0% (same)
    current : value between minimum and maximum.
        How to compute the current percentage : (current - minimum) / (maximum - minimum)
        You should then multiply by 100 to get an actual percentage.
    line_color : a 4-tuple corresponding to the gauge's color.
    line_width : the width of the gauge.
    border_color : a 4-tuple corresponding to the gauge's borders' color.
    gauge_background_color : a 4-tuple representing the color to apply where the gauge is empty.
    image_background_color : a 4-tuple representing the color to apply under the image.
    resize : if True, will resize the image with the width and height times SQUARE.
    shape : if "square", will return the image with squared gauge. If "circle", will return the image with circled gauge. 
    """
    

    def __init__(self, master : MasterBox, X : int, Y : int, width : int, height : int, image : str, maximum : float, minimum : float, current : float,
                 line_color : tuple = (255, 0, 0, 255), line_width : int = 4, border_color : tuple = BORDER_COLOR, gauge_background_color : tuple = BACKGROUND_COLOR,
                 image_background_color : tuple = BACKGROUND_COLOR2, resize : bool = True, shape : str = "circle") :
        
        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if X + width > master.width :
            raise BoxSizeError("X + width")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if Y + height > master.height :
            raise BoxSizeError("Y + height")

        if shape not in ("square", "circle") :
            raise StringArgumentError(shape)
        

        self.master = master
        
        self.X, self.Y = X, Y
        self.width, self.height = width * SQUARE, height * SQUARE
        self.expected_size = (width, height)
        
        self.image = image
        self.percentage = percent(maximum, minimum, current)
        
        self.line_color = line_color
        self.line_width = line_width
        self.border_color = border_color
        self.gauge_background_color = gauge_background_color
        self.image_background_color = image_background_color

        self.resize = resize

        self.shape = shape

        master.add_box(self)



    def get_image(self) :

        im = Image.open(self.image)
        if self.resize :
            im = im.resize((self.width, self.height))

        #- Squared AvatarBox -------------------------------------------------------------------------------------------------------------------
        if self.shape == "square" :

            rectangles = Image.new("RGBA", im.size, (0,0,0,0))
            gauge = ImageDraw.Draw(rectangles)
        
            gauge.rectangle( ((0, 0), (im.size[0] - 1, im.size[1] - 1)), outline = self.border_color, fill = self.gauge_background_color ) 
            a = 1+self.line_width
            gauge.rectangle( ((a, a), (im.size[0]-a-1, im.size[1]-a-1)), outline = self.border_color, fill = (0,0,0,0) )


            if self.percentage > 0 :
                gauge.rectangle( ( (int(im.size[0]/2), 1), (int(im.size[0]/2) + int((im.size[0]/2)-2-self.line_width) * percent(0.125, 0, self.percentage), self.line_width) ),
                                 fill = self.line_color)
                
                if self.percentage > 0.125 :
                    gauge.rectangle( ( (im.size[0]-a, 1), (im.size[0]-2, int((im.size[1]-2-self.line_width) * percent(0.375, 0.125, self.percentage))) ),
                              fill = self.line_color)

                    if self.percentage > 0.375 :
                        gauge.rectangle( ( (im.size[0]-2, im.size[1]-a), (1 + self.line_width + int((im.size[0]-1) * (1 - percent(0.625, 0.375, self.percentage))), im.size[1]-2) ), 
                                  fill = self.line_color)
                        

                        if self.percentage > 0.625 :
                            gauge.rectangle( ( (1, im.size[1]-2), (self.line_width, 1 + self.line_width + int((im.size[1]-1) * (1 - percent(0.875, 0.625, self.percentage)))) ), 
                                      fill = self.line_color)
                            

                            if self.percentage > 0.875 :
                                gauge.rectangle( ( (1, 1), (int((im.size[0]/2)) * percent(1, 0.875, self.percentage)), self.line_width) , 
                                          fill = self.line_color)



            gauge = ImageDraw.Draw(rectangles)

            im.paste(rectangles, (0,0), rectangles)
            back = Image.new("RGBA", im.size, self.image_background_color)
            back.paste(im, (0,0), im)



        #- Circled AvatarBox -------------------------------------------------------------------------------------------------------------------
        if self.shape == "circle" :

            circles = Image.new("RGBA", im.size, (0,0,0,0))
            gauge = ImageDraw.Draw(circles)

            gauge.ellipse( ((0,0), (im.size[0] - 1, im.size[1] - 1)), outline = self.border_color, fill = self.gauge_background_color)
            a = self.line_width + 1
            gauge.ellipse( ((a,a), (im.size[0]-a-1, im.size[1]-a-1)), outline = self.border_color, fill = (0,0,0,0))

            angle = int(360 * percent(1, 0, self.percentage)) - 90
            for i in range(self.line_width) :
                gauge.arc( ((1+i, 1+i), (im.size[0]-i-2, im.size[1]-i-2)), start = -90, end = angle, fill = self.line_color)

            gauge = ImageDraw.Draw(circles)

            back = Image.new("RGBA", im.size, (0,0,0,0))
            gauge = ImageDraw.Draw(back)
            gauge.ellipse( ((0,0), (im.size[0]-1, im.size[1]-1)), fill = self.image_background_color, outline = self.image_background_color)
            gauge = ImageDraw.Draw(back)

            im.paste(circles, (0,0), circles)
            back.paste(im, (0,0), back)


        return back


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#
#   GaugeBox
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class GaugeBox(object) :

    """
    master, X, Y : do I need to explain these parameters again ?
    length : width or height (depending on orient parameter). Other size parameter is set to 1.
    orient : "horizontal" or "vertical". If horizontal, length is width, otherwise height.
    maximum : 100%
    minimum : 0%
    current : a value between maximum and minimum. The gauge is filled with the percentage of current in the scale defined by minimum and maximum.
    line_width : width of gauge, in pixels.
    line_color : its color. If you want a color which changes with the percentage of current, see percent_color function.
    border_color : explicit, no ?
    background_image : color of the gauge where it's not filled.
    steps : a float between 0 and 1 representing the percentage of mini-bar. For example, if you put 0.1 to steps, there will be 10 mini-bars and each one will take 10% of the great one.
    margin : space (in pixels) between bar and square just below.
    name : for exemple, if you make a HP gauge, put 'HP' in name.
    name_color : color for name.
    name_font : as usual. If the second element is too big, it will be resized at the greatest possible value.
    maximum_text : like name but is displayed at the maximum of the gauge.
    maximum_color : same as name_color but for maximum.
    maximum_font : same as name_font.
    """
    

    def __init__(self, master : MasterBox, X : int, Y : int, length : int, orient : str, maximum : float, minimum : float, current : float,
                 line_width : int = 6, line_color : tuple = (255, 0, 0, 255), border_color : tuple = BORDER_COLOR, background_color : tuple = BACKGROUND_COLOR,
                 steps : float = 1, margin : int = 3, name : str = "", name_color : tuple = (0,0,0,255), name_font : tuple = FONT,
                 maximum_text : str = "", maximum_color : tuple = (0,0,0,255), maximum_font : tuple = FONT) :

        if orient not in ("horizontal", "vertical") :
            raise StringArgumentError(orient)

        if X < 0 or X >= master.width :
            raise BoxIndexError(X, master.width)
        if orient == "horizontal" and X + length > master.width :
            raise BoxSizeError("X + width")
        
        if Y < 0 or Y >= master.height :
            raise BoxIndexError(Y, master.height)
        if orient == "vertical" and Y + length > master.height :
            raise BoxSizeError("Y + height")
        

        self.master = master
        
        self.X, self.Y = X, Y
        self.length = length * SQUARE
        self.orient = orient
        if orient == "horizontal" :
            self.expected_size = (length, 1)
        else :
            self.expected_size = (1, length)
        
        self.percentage = percent(maximum, minimum, current)
        
        self.line_color = line_color
        self.line_width = line_width
        self.border_color = border_color
        self.background_color = background_color

        if steps > 1 :
            steps = 1
        elif steps < 0 :
            steps = 0
        self.steps = steps
        
        if margin < 0 :
            margin = 0
        self.margin = margin

        self.name = name
        self.name_color = name_color
        if name_font[1] > SQUARE - line_width - 2 - margin :
            name_font = (name_font[0], SQUARE - line_width - 2 - margin)
        self.name_font = name_font

        self.maximum_text = maximum_text
        self.maximum_color = maximum_color
        if maximum_font[1] > SQUARE - line_width - 2 - margin :
            maximum_font = (maximum_font[0], SQUARE - line_width - 2 - margin)
        self.maximum_font = maximum_font

        master.add_box(self)



    def get_image(self) :

        im = Image.new("RGBA", (self.length, SQUARE), (0,0,0,0))

        draw = ImageDraw.Draw(im)
        x = 2 * self.line_width
        y = im.size[1] - self.margin - self.line_width

        draw.polygon( polygon(( (x, y), (im.size[0]-x, im.size[1]-self.margin) )), fill = self.background_color, outline = self.border_color)
        draw.polygon( polygon(( (x+1, y+1), ( (im.size[0]-2*x-2)*self.percentage+x+1, im.size[1]-self.margin-1) )), fill = self.line_color)

        if self.name_font not in self.master.memorizer["fonts"].keys() :
            self.master.memorizer["fonts"][self.name_font] = ImageFont.truetype(FONT_PATH + self.name_font[0], self.name_font[1])
        if self.maximum_font not in self.master.memorizer["fonts"].keys() :
            self.master.memorizer["fonts"][self.maximum_font] = ImageFont.truetype(FONT_PATH + self.maximum_font[0], self.maximum_font[1])


        for i in float_range( 0, 1, self.steps ) :
            a = int(reci_percent(im.size[0]-x, x, i))
            draw.line( ((a, y), (a, im.size[1]-self.margin)), fill = self.border_color)


        a = draw.textsize(self.name, self.master.memorizer["fonts"][self.name_font])
        b  = SQUARE - self.line_width - 2 - self.margin
        draw.text( (x, int((b - a[1])/2)), self.name, font = self.master.memorizer["fonts"][self.name_font], fill = self.name_color)
        a = draw.textsize(self.maximum_text, self.master.memorizer["fonts"][self.maximum_font])
        draw.text( (im.size[0] - a[0] - x, b - a[1]), self.maximum_text,
                   font = self.master.memorizer["fonts"][self.maximum_font], fill = self.maximum_color)
        
            
        if self.orient == "vertical" :
            draw = ImageDraw.Draw(im)
            
            a = int(im.size[0]/2)
            im = im.crop( (0, -a, im.size[0], a ) )
            im = im.rotate(90)
            im = im.crop( (a, 0, a + SQUARE, im.size[1]) )

        draw = ImageDraw.Draw(im)


        return im
