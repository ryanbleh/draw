import random
import time
import math
import json 
"""
This is a simple interactive graphics and animation library for Python.
Author: ####
Version: 4.1.0 (last updated January, 2021)

This code is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike license
see http://creativecommons.org/licenses/by-nc-sa/3.0/ for details

Note: You must have the pygame library installed for this to work.
        You can read about pygame at http://www.pygame.org/.

This has been tested with Python 3.0.0 and Pygame 2.0.0.
"""

print()
print("using graphics.py library version 4.1.0")

import pygame, sys, os, math, os.path

print("using pygame version " + pygame.version.ver)
print()

sys.stdout.flush()

class World:
    pass

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class GameLibInfo:
    def __init__(self):
        self.initialize()
        
    def initialize(self):
        self.world = None
        self.graphicsInited = False
        self.fonts = dict()
        self.macFonts = None
        self.defaultFont = None
        self.defaultFontSize = 30
        self.eventListeners = dict()
        self.imageCache = dict()
        self.frameRate = 60
        self.windowWidth = 0
        self.windowHeight = 0
        self.background = (255,255,255)
        self.foreground = (0,0,0)
        self.nextEventType = pygame.USEREVENT
        self.keysPressedNow = dict()
        self.FPStime = 0
        self.FPSinterval = 0
        self.FPScount = 0
        self.joysticks = []
        self.joystickLabels = []  # list of dictionaries
        self.numJoysticks = 0
        self.joystickDeadZone = 0.05
        self.joystickLabelDefault = [["X", "Y"]]
        self.joystickLabelDefaults = {
            "Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Logitech Logitech Dual Action" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech RumblePad 2 USB" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Cordless RumblePad 2" : [["X","Y"], ["LeftX", "LeftY", "RightX", "RightY"]],
            "Logitech Logitech Attack 3" : [["X", "Y", "Throttle"]],

            "Controller (Gamepad F310)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],
            "Controller (Wireless Gamepad F710)" : [["X","Y"], ["LeftX","LeftY","Trigger","RightY","RightX"]],

            "Saitek Aviator Stick" : [["X", "Y", "LeftThrottle", "Twist", "RightThrottle"]],
            "Saitek AV8R Joystick" : [["X", "Y", "Twist", "LeftThrottle", "RightThrottle"]],
            "Saitek Pro Flight Throttle Quadrant" : [["LeftThrottle", "CenterThrottle", "RightThrottle"]],

            "XBOX 360 For Windows (Controller)" : [["X","Y"], ["LeftX", "LeftY", "Trigger", "RightY", "RightX"]]

            }


    def initializeListeners(self):
        #onKeyPress(lambda world,key: 0)
        #onKeyRelease(lambda world,key: 0)
        onAnyKeyPress(lambda world,key: 0)
        onAnyKeyRelease(lambda world,key: 0)
        onMousePress(lambda world,x,y,button: 0)
        onMouseRelease(lambda world,x,y,button: 0)
        onWheelForward(lambda world,x,y: 0)
        onWheelBackward(lambda world,x,y: 0)
        onMouseMotion(lambda world,x,y,dx,dy,b1,b2,b3: 0)
        onGameControllerStick(lambda world,device,axis,value: 0)
        onGameControllerDPad(lambda world,device,pad,xvalue,yvalue: 0)
        onGameControllerButtonPress(lambda world,device,button: 0)
        onGameControllerButtonRelease(lambda world,device,button: 0)

    def initializeJoysticks(self):
        self.numJoysticks = pygame.joystick.get_count()
        for id in range(self.numJoysticks):
            self.joysticks.append(pygame.joystick.Joystick(id))
            self.joystickLabels.append(dict())
            self.joysticks[id].init()
            stickname = self.joysticks[id].get_name()
            if stickname in self.joystickLabelDefaults:
                print("recognized a " + stickname)
                labelList = self.joystickLabelDefaults[stickname]
            else:
                print("unknown game controller: " + stickname)
                labelList = self.joystickLabelDefault
            for labels in labelList:
                gameControllerSetStickAxesNames(labels, id)
            print("    with axes: ", gameControllerGetStickAxesNames())

    def startGame(self):
        self.clock = pygame.time.Clock()
        self.startTime = pygame.time.get_ticks()
        self.keepRunning = True

    def maybePrintFPS(self):
        self.FPScount += 1
        if self.FPSinterval > 0:
            time = pygame.time.get_ticks()
            if time > self.FPStime + self.FPSinterval:
                print(getActualFrameRate())
                self.FPStime = time
                self.FPScount = 0

    def loadColors(self, colorsList):
        self.colorsList = colorsList
        self.colorTable = dict()
        for (name, red, green, blue, hexcolor) in colorsList:
            self.colorTable[name] = (int(red),int(green),int(blue))

    def loadKeys(self, keyList):
        self.keyList = keyList
        self.key2nameDict = dict()
        self.name2keyDict = dict()
        for (code, nameList) in keyList:
            self.key2nameDict[code] = nameList[0].lower()
            for name in nameList:
                self.name2keyDict[name.lower()] = code

        
_GLI = GameLibInfo()

def makeGraphicsWindow(width, height, fullscreen=False, position=None):
    initGraphics()
    
    if position is None:
        os.environ['SDL_VIDEO_CENTERED'] = 'center'
    else:
        (x,y) = position
        os.environ['SDL_VIDEO_WINDOW_POS'] = str(x)+','+str(y)
    
    setGraphicsMode(width, height, fullscreen)

def initGraphics():
    if _GLI.graphicsInited == False:        
        pygame.init()
        _GLI.initialize()
        _GLI.initializeListeners()
        _GLI.initializeJoysticks()
        _GLI.graphicsInited = True
    
def endGraphics():
    _GLI.keepRunning = False

def setGraphicsMode(width, height, fullscreen=False):
    _GLI.windowWidth = width
    _GLI.windowHeight = height
    flags = 0
    if fullscreen == True:
        flags = flags | pygame.FULLSCREEN # | pygame.DOUBLEBUF | pygame.HWSURFACE 
    #flags = flags | pygame.HWSURFACE | pygame.DOUBLEBUF
    _GLI.screen = pygame.display.set_mode((width, height), flags)

def getScreenSize():
    initGraphics()
    info = pygame.display.Info()
    return (info.current_w, info.current_h)

def getAllScreenSizes():
    initGraphics()
    return pygame.display.list_modes()

def setBackground(background):
    if isinstance(background, str):
        _GLI.background = lookupColor(background)
    else:
        _GLI.background = background

def setForeground(foreground):
    _GLI.foreground = foreground

def getActualFrameRate():
    return _GLI.clock.get_fps()

def displayFPS(interval):
    _GLI.FPSinterval = interval*1000
    _GLI.FPStime = pygame.time.get_ticks()
    _GLI.FPScount = 0

def getWindowWidth():
    return _GLI.windowWidth

def getWindowHeight():
    return _GLI.windowHeight

def setWindowTitle(title):
    pygame.display.set_caption(str(title))


def lookupColor(color):
    if color in _GLI.colorTable:
        return _GLI.colorTable[color]
    else:
        return color

def getColorsList():
    return [color[0] for color in _GLI.colorsList]

def getColorsDetailList():
    return [color for color in _GLI.colorsList]


###################################################################

def drawPixel(x, y, color=_GLI.foreground):
    _GLI.screen.set_at((int(x),int(y)), lookupColor(color))

def drawLine(x1, y1, x2, y2, color=_GLI.foreground, thickness=1):
    pygame.draw.line(_GLI.screen, lookupColor(color), (int(x1),int(y1)), (int(x2),int(y2)), int(thickness))

def drawCircle(x, y, radius, color=_GLI.foreground, thickness=1):
    pygame.draw.circle(_GLI.screen, lookupColor(color), (int(x),int(y)), int(radius), int(thickness))

def fillCircle(x, y, radius, color=_GLI.foreground):
    drawCircle(x, y, radius, color, 0)

def drawEllipse(x, y, width, height, color=_GLI.foreground, thickness=1):
    pygame.draw.ellipse(_GLI.screen, lookupColor(color), pygame.Rect(int(x-width/2), int(y-height/2), int(width), int(height)), int(thickness))

def fillEllipse(x, y, width, height, color=_GLI.foreground):
    drawEllipse(x, y, width, height, color, 0)

def drawArcCircle(x, y, radius, startAngle, endAngle, color=_GLI.foreground, thickness=1):
    drawArcEllipse(x, y, radius*2, radius*2, startAngle, endAngle, color, thickness)

def drawArcEllipse(x, y, width, height, startAngle, endAngle, color=_GLI.foreground, thickness=1):
    minAngle = math.radians(min(startAngle, endAngle))
    maxAngle = math.radians(max(startAngle, endAngle))
    pygame.draw.arc(_GLI.screen, lookupColor(color), pygame.Rect(int(x-width/2), int(y-height/2), int(width), int(height)), minAngle, maxAngle, thickness)


def drawRectangle(x, y, width, height, color=_GLI.foreground, thickness=1):
    pygame.draw.rect(_GLI.screen, lookupColor(color), pygame.Rect(int(x),int(y),int(width),int(height)), int(thickness))

def fillRectangle(x, y, width, height, color=_GLI.foreground):
    drawRectangle(x, y, width, height, color, 0)

def drawPolygon(pointlist, color=_GLI.foreground, thickness=1):
    pygame.draw.polygon(_GLI.screen, lookupColor(color), pointlist, int(thickness))
    
def fillPolygon(pointlist, color=_GLI.foreground):
    drawPolygon(pointlist, color, 0)
    
def drawLines(pointlist, color=_GLI.foreground, thickness=1):
    pygame.draw.lines(_GLI.screen, lookupColor(color), False, pointlist, int(thickness))

    
####

def sizeString(text, size=None, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    textimage = font.render(str(text), False, (1,1,1))
    return (textimage.get_width(), textimage.get_height())

def widthString(text, size=None, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    textimage = font.render(str(text), False, (1,1,1))
    return textimage.get_width()

def heightString(text, size=None, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    textimage = font.render(str(text), False, (1,1,1))
    return textimage.get_height()

def drawString(text, x, y, size=None, color=_GLI.foreground, bold=False, italic=False, font=None):
    font = _getFont(font, size, bold, italic)
    color = lookupColor(color)
    textimage = font.render(str(text), False, color)
    _GLI.screen.blit(textimage, (int(x), int(y)))
    return (textimage.get_width(), textimage.get_height())

def getFontList():
    if sys.platform != 'darwin':
        return pygame.font.get_fonts()
    else:
        _initMacFonts()
        return sorted(_GLI.macFonts.keys())

def setDefaultFont(font, size=None):
    _GLI.defaultFont = font
    if size is not None:
        _GLI.defaultFontSize = size

def _getFont(font, size, bold, italic):
    if font is None and _GLI.defaultFont is not None:
        font = _GLI.defaultFont
    if size is None:
        size = _GLI.defaultFontSize
    fontSignature = (font,size,bold,italic)
    if fontSignature in _GLI.fonts:
        font = _GLI.fonts[fontSignature]
    else:
        extensions = ('.ttf', '.ttc', '.otf', '.dfont')
        if font is not None and font.endswith(extensions):
            font = _loadFontFile(font, size)
        else:
            if sys.platform != 'darwin':
                font = pygame.font.SysFont(font, size, bold, italic)
            else:
                _initMacFonts()
                if font in _GLI.macFonts:
                    font = _GLI.macFonts[font]
                font = _loadFontFile(font, size)
        _GLI.fonts[fontSignature] = font
    return font

def _loadFontFile(font, size):
    try:
        font = pygame.font.Font(font, size)
    except IOError:
        print("Failed to load font: " + font)
        font = pygame.font.Font(None, size)
    return font

# used on Macs as long as pygame's font handling is broken
def _initMacFonts():
    if _GLI.macFonts is not None: return
    _GLI.macFonts = dict()
    folders = ['/System/Library/Fonts', '/Library/Fonts']
    if 'HOME' in os.environ:
        folders.append(os.environ['HOME'] + '/Library/Fonts')
    extensions = ('.ttf', '.ttc', '.otf', '.dfont')
    for folder in folders:
        if not os.path.isdir(folder): continue
        files = os.listdir(folder)
        for filename in files:
            if filename.endswith(extensions):
                dot = filename.rfind('.')
                fontname = filename[:dot]
                _GLI.macFonts[fontname] = os.path.join(folder, filename)
                

#########################################################

def loadImage(filename, transparentColor=None, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):

    imageKey = (filename, transparentColor, rotate, scale, flipHorizontal, flipVertical)
    if imageKey in _GLI.imageCache:
        return _GLI.imageCache[imageKey]

    if transparentColor == None:
        image = pygame.image.load(filename).convert_alpha()
    else:
        image = pygame.image.load(filename).convert();
        if transparentColor != False:
            image.set_colorkey(lookupColor(transparentColor))
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        if scale > 10:
            raise Exception("Do not scale an image to more than 10x its original size")        
        image = pygame.transform.rotozoom(image, rotate, scale)

    _GLI.imageCache[imageKey] = image

    return image

def loadImagePIL(pilImage):
    pilImage = pilImage.convert("RGBA")
    return pygame.image.frombuffer(pilImage.tobytes(), pilImage.size, pilImage.mode)

def drawImage(image, x, y, rotate=0, scale=1, flipHorizontal=False, flipVertical=False):
    if flipHorizontal or flipVertical:
        image = pygame.transform.flip(image, flipHorizontal, flipVertical)
    if rotate != 0 or scale != 1:
        if scale > 10:
            raise Exception("Do not scale an image to more than 10x its original size")        
        image = pygame.transform.rotozoom(image, rotate, scale)
    _GLI.screen.blit(image, (int(x-image.get_width()/2),int(y-image.get_height()/2)))

def getImageWidth(image):
    return image.get_width()

def getImageHeight(image):
    return image.get_height()

def getImagePixel(image, x, y):
    return image.get_at((int(x),int(y)))

def getScreenPixel(x, y):
    if x < 0 or x >= _GLI.windowWidth or y < 0 or y >= _GLI.windowHeight:
        return None
    return _GLI.screen.get_at((int(x),int(y)))

def getImageRegion(image, x, y, width, height):
    return image.subsurface(pygame.Rect(int(x),int(y),int(width),int(height)))

def saveImage(image, filename):
    pygame.image.save(image,filename)

def saveScreen(filename):
    pygame.image.save(_GLI.screen,filename)

#########################################################

def loadSound(filename, volume=1):
    sound = pygame.mixer.Sound(filename)
    if volume != 1:
        sound.set_volume(volume)
    return sound

def playSound(sound, repeat=False):
    if repeat:
        sound.play(-1)
    else:
        sound.play()

def stopSound(sound):
    sound.stop()

def loadMusic(filename, volume=1):
    pygame.mixer.music.load(filename)
    if volume != 1:
        pygame.mixer.music.set_volume(volume)

def playMusic(repeat=False):
    if repeat:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play()

def stopMusic():
    pygame.mixer.music.stop()

#########################################################


def onKeyPress(listenerFunction, key):
    key = getKeyCode(key)
    if key is None:
        raise Exception("that is not a valid key")
    _GLI.eventListeners[("keydown",key)] = listenerFunction

def onAnyKeyPress(listenerFunction):
    _GLI.eventListeners["keydown"] = listenerFunction

def onKeyRelease(listenerFunction, key):
    key = getKeyCode(key)
    if key == None:
        raise Exception("that is not a valid key")
    _GLI.eventListeners[("keyup",key)] = listenerFunction

def onAnyKeyRelease(listenerFunction):
    _GLI.eventListeners["keyup"] = listenerFunction


    
def onMousePress(listenerFunction):
    _GLI.eventListeners["mousedown"] = listenerFunction
    
def onMouseRelease(listenerFunction):
    _GLI.eventListeners["mouseup"] = listenerFunction

def onWheelForward(listenerFunction):
    _GLI.eventListeners["wheelforward"] = listenerFunction

def onWheelBackward(listenerFunction):
    _GLI.eventListeners["wheelbackward"] = listenerFunction

def onMouseMotion(listenerFunction):
    _GLI.eventListeners["mousemotion"] = listenerFunction

def onGameControllerStick(listenerFunction):
    _GLI.eventListeners["stickmotion"] = listenerFunction
    
def onGameControllerDPad(listenerFunction):
    _GLI.eventListeners["dpadmotion"] = listenerFunction
    
def onGameControllerButtonPress(listenerFunction):
    _GLI.eventListeners["joybuttondown"] = listenerFunction
    
def onGameControllerButtonRelease(listenerFunction):
    _GLI.eventListeners["joybuttonup"] = listenerFunction

def onTimer(listenerFunction, interval):
    if _GLI.nextEventType > pygame.NUMEVENTS:
        raise ValueError("too many timer listeners")
    _GLI.eventListeners["timer" + str(_GLI.nextEventType)] = listenerFunction
    pygame.time.set_timer(_GLI.nextEventType, interval)
    _GLI.nextEventType += 1

#########################################################

def getMousePosition():
    return pygame.mouse.get_pos()

def getMouseButton(button):
    return pygame.mouse.get_pressed()[button-1]

def hideMouse():
    pygame.mouse.set_visible(False)

def showMouse():
    pygame.mouse.set_visible(True)

def moveMouse(x, y):
    pygame.mouse.set_pos((int(x), int(y)))

def isKeyPressed(key):
    key = getKeyCode(key)
    return _GLI.keysPressedNow.get(key, False)

def getKeyName(key):
    if key in _GLI.key2nameDict:
        return _GLI.key2nameDict[key]
    else:
        return None

def getKeyCode(key):
    if key is None:
        return None
    if key in _GLI.key2nameDict:
        return key
    key = key.lower()
    if key in _GLI.name2keyDict:
        return _GLI.name2keyDict[key]
    else:
        return None

def sameKeys(key1, key2):
    code1 = getKeyCode(key1)
    code2 = getKeyCode(key2)
    if code1 is None:
        raise Exception("unknown key name: " + key1)
    if code2 is None:
        raise Exception("unknown key name: " + key2)
    return code1 == code2

#########################################################

def numGameControllers():
    return _GLI.numJoysticks

def gameControllerNumStickAxes(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numaxes()
    else:
        return 0

def gameControllerNumDPads(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numhats()
    else:
        return 0

def gameControllerNumButtons(device=0):
    if device < _GLI.numJoysticks:
        return _GLI.joysticks[device].get_numbuttons()
    else:
        return 0

def gameControllerSetDeadZone(deadzone):
    _GLI.joystickDeadZone = deadzone

def gameControllerGetStickAxesNames(device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        axes = list(labelDict.keys())
        axes.sort(key=lambda axis: labelDict[axis])
        return axes
    return []

def gameControllerStickAxis(axis, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        labelDict = _GLI.joystickLabels[device]
        if axis in labelDict:
            axis = labelDict[axis]
        elif isinstance(axis, str):
            raise RuntimeError("unknown game controller axis: " + str(axis))
        if axis < joystick.get_numaxes():
            value = joystick.get_axis(axis)
            if abs(value) > _GLI.joystickDeadZone:
                return value
    return 0            

def gameControllerSetStickAxesNames(axesList, device=0):
    if device < _GLI.numJoysticks:
        labelDict = _GLI.joystickLabels[device]
        for i in range(len(axesList)):
            labelDict[axesList[i]] = i
        
def gameControllerButton(button, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        button -= 1
        if button >= 0 and button < joystick.get_numbuttons():
            value = joystick.get_button(button)
            return (value == 1)
    return False            

def gameControllerDPadX(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dx
    return 0            

def gameControllerDPadY(dpad=0, device=0):
    if device < _GLI.numJoysticks:
        joystick = _GLI.joysticks[device]
        if dpad < joystick.get_numhats():
            (dx,dy) = joystick.get_hat(dpad)
            return dy
    return 0            

#########################################################
# Math functions

def convertToComponents(angle, length):
    angle = math.radians(angle)
    dx = length * math.cos(angle)
    dy = length * -math.sin(angle)
    return (dx,dy)

def convertToAngle(x, y):
    angle = math.degrees(math.atan2(-y, x))
    while angle < 0:
        angle += 360
    return angle

# for backwards compatibility
cartesianToPolarAngle = convertToAngle
polarToCartesian = convertToComponents

def pointInPolygon(x, y, polygon):
    # original author: W. Randolph Franklin
    # source: http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html
    inside = False
    length = len(polygon)
    i = 0
    j = length - 1
    while i < length:
        (vix,viy) = polygon[i]
        (vjx,vjy) = polygon[j]
        if (( (viy > y) != (vjy > y) ) and
            (x < (vjx-vix) * (y-viy) / float(vjy-viy) + vix) ):
            inside = not inside
        j = i
        i += 1
    return inside
        
    
            
#########################################################

# use animate for non-interactive animations
def animate(drawFunction, timeLimit, repeat=False):
    def startAnimation(world):
        pass
    def timeExpired(world):
        if getElapsedTime() >= timeLimit:
            if repeat:
                resetTime()
            else:
                _GLI.keepRunning = False
    def drawAnimationFrame(world):
        drawFunction(float(getElapsedTime()))
    runGraphics(startAnimation, timeExpired, drawAnimationFrame)



# use runGraphics for interactive programs like games
def runGraphics(startFunction, updateFunction, drawFunction, quit=True):
    try:
        _GLI.startGame()
        _GLI.world = World()
        startFunction(_GLI.world)
        while _GLI.keepRunning:
            eventlist = pygame.event.get()
            for event in eventlist:
                if event.type == pygame.QUIT:
                    _GLI.keepRunning = False
                    break
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        _GLI.keepRunning = False
                        break
                    else:
                        _GLI.keysPressedNow[event.key] = True
                        if ("keydown",event.key) in _GLI.eventListeners:
                            _GLI.eventListeners[("keydown",event.key)](_GLI.world)
                        else:
                            _GLI.eventListeners["keydown"](_GLI.world, event.key)
                            
                elif event.type == pygame.KEYUP:
                    _GLI.keysPressedNow[event.key] = False
                    if ("keyup",event.key) in _GLI.eventListeners:
                        _GLI.eventListeners[("keyup",event.key)](_GLI.world)
                    else:
                        _GLI.eventListeners["keyup"](_GLI.world, event.key)
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button <= 3:
                        _GLI.eventListeners["mousedown"](_GLI.world, event.pos[0], event.pos[1], event.button)
                    elif event.button == 4:
                        _GLI.eventListeners["wheelforward"](_GLI.world, event.pos[0], event.pos[1])
                    elif event.button == 5:
                        _GLI.eventListeners["wheelbackward"](_GLI.world, event.pos[0], event.pos[1])
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button <= 3:
                        _GLI.eventListeners["mouseup"](_GLI.world, event.pos[0], event.pos[1], event.button)
                elif event.type == pygame.MOUSEMOTION:
                    if event.rel[0] != 0 or event.rel[1] != 0:
                        button1 = (event.buttons[0] == 1)
                        button2 = (event.buttons[1] == 1)
                        button3 = (event.buttons[2] == 1)
                        _GLI.eventListeners["mousemotion"](_GLI.world, event.pos[0],event.pos[1],event.rel[0],event.rel[1],button1,button2,button3)

                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) < _GLI.joystickDeadZone:
                        joystickValue = 0
                    else:
                        joystickValue = event.value
                    _GLI.eventListeners["stickmotion"](_GLI.world, event.joy, event.axis, joystickValue)
                elif event.type == pygame.JOYHATMOTION:
                    _GLI.eventListeners["dpadmotion"](_GLI.world, event.joy, event.hat, event.value[0], event.value[1])
                elif event.type == pygame.JOYBUTTONUP:
                    _GLI.eventListeners["joybuttonup"](_GLI.world, event.joy, event.button+1)
                elif event.type == pygame.JOYBUTTONDOWN:
                    _GLI.eventListeners["joybuttondown"](_GLI.world, event.joy, event.button+1)
                    
                elif event.type >= pygame.USEREVENT:   # timer event
                    _GLI.eventListeners["timer"+str(event.type)](_GLI.world)
                    
            updateFunction(_GLI.world)
            if isinstance(_GLI.background, pygame.Surface):
                _GLI.screen.blit(_GLI.background, (0,0))
            elif _GLI.background != None:
                _GLI.screen.fill(_GLI.background)
            drawFunction(_GLI.world)
            pygame.display.flip()
            _GLI.maybePrintFPS()
            _GLI.clock.tick(_GLI.frameRate)
    finally:
        if quit:
            pygame.quit()

def closeGraphicsWindow():
    pygame.display.quit()

def quit():
    pygame.quit()

def getWorld():
    return _GLI.world

def getElapsedTime():
    return pygame.time.get_ticks() - _GLI.startTime

def resetTime():
    _GLI.startTime = pygame.time.get_ticks()

def setFrameRate(frameRate):
    _GLI.frameRate = frameRate

#########################################################

# these functions are intended for use in non-animated graphics programs

##def redrawWindow():
##    pygame.display.update()
##    checkForWindowClosing()
##
##def checkForWindowClosing():
##    if pygame.event.peek(pygame.QUIT):
##        quitGraphics()
##            
##def waitForWindowClosing():
##    while True:
##        event = pygame.event.wait()
##        if event.type == pygame.QUIT:
##            quitGraphics()
##
##def waitForMouseClick():
##    while True:
##        event = pygame.event.wait()
##        if event.type == pygame.QUIT:
##            quitGraphics()
##        elif event.type == pygame.MOUSEBUTTONDOWN:
##            return event.pos
##
##def waitForKeyPress():
##    while True:
##        event = pygame.event.wait()
##        if event.type == pygame.QUIT:
##            quitGraphics()
##        elif event.type == pygame.KEYDOWN:
##            return chr(event.key)
##
##def quitGraphics():
##     pygame.quit()
##     sys.exit()

#########################################################
#########################################################

def makeColorsWebPage():
    web = file("colors.html", "w")
    web.write("""<html><head><title>Python Colors</title></head>
                 <body><center>
                 <h1>Color Names and Values</h1>
                 <table>
              """)
    count = 0
    for (name, red, green, blue, hexcode) in _GLI.colorsList:
        if count % 4 == 0:
            if count > 0:
                web.write('</tr>')
            web.write('<tr>\n')   
        fontcolor = '#000000'
        r = int(red)
        g = int(green)
        b = int(blue)
        if (r+g+b) < 250:
            fontcolor = '#FFFFFF'
        web.write("""<td bgcolor="%s" align=center width=200 height=75>
                  <font color="%s"><b>%s<br>(%d,%d,%d)</b></font></td>""" % (hexcode, fontcolor, name, r, g, b))
        count = count+1
    web.write('</tr></table></center></body></html>')
    web.close()

def makeKeysWebPage():
    web = file("keys.html", "w")
    web.write("""<html><head><title>Python Keys</title></head>
                 <body><center>
                 <h1>Key Names</h1>
                 <table>
              """)
    count = 0

    for (code, nameList) in _GLI.keyList:
        web.write('<tr>')
        for name in nameList:
            web.write('<td>' + name + '</td>')
        web.write('</tr>')
    web.write('</table></center></body></html>')
    web.close()

_GLI.loadColors([\
("aliceblue",240,248,255,"#f0f8ff"),\
("antiquewhite",250,235,215,"#faebd7"),\
("aqua",0,255,255,"#00ffff"),\
("aquamarine",127,255,212,"#7fffd4"),\
("azure",240,255,255,"#f0ffff"),\
("beige",245,245,220,"#f5f5dc"),\
("bisque",255,228,196,"#ffe4c4"),\
("black",0,0,0,"#000000"),\
("blanchedalmond",255,235,205,"#ffebcd"),\
("blue",0,0,255,"#0000ff"),\
("blueviolet",138,43,226,"#8a2be2"),\
("brown",165,42,42,"#a52a2a"),\
("burlywood",222,184,135,"#deb887"),\
("cadetblue",95,158,160,"#5f9ea0"),\
("chartreuse",127,255,0,"#7fff00"),\
("chocolate",210,105,30,"#d2691e"),\
("coral",255,127,80,"#ff7f50"),\
("cornflowerblue",100,149,237,"#6495ed"),\
("cornsilk",255,248,220,"#fff8dc"),\
("crimson",220,20,60,"#dc143c"),\
("cyan",0,255,255,"#00ffff"),\
("darkblue",0,0,139,"#00008b"),\
("darkcyan",0,139,139,"#008b8b"),\
("darkgoldenrod",184,134,11,"#b8860b"),\
("darkgray",169,169,169,"#a9a9a9"),\
("darkgreen",0,100,0,"#006400"),\
("darkgrey",169,169,169,"#a9a9a9"),\
("darkkhaki",189,183,107,"#bdb76b"),\
("darkmagenta",139,0,139,"#8b008b"),\
("darkolivegreen",85,107,47,"#556b2f"),\
("darkorange",255,140,0,"#ff8c00"),\
("darkorchid",153,50,204,"#9932cc"),\
("darkred",139,0,0,"#8b0000"),\
("darksalmon",233,150,122,"#e9967a"),\
("darkseagreen",143,188,143,"#8fbc8f"),\
("darkslateblue",72,61,139,"#483d8b"),\
("darkslategray",47,79,79,"#2f4f4f"),\
("darkslategrey",47,79,79,"#2f4f4f"),\
("darkturquoise",0,206,209,"#00ced1"),\
("darkviolet",148,0,211,"#9400d3"),\
("deeppink",255,20,147,"#ff1493"),\
("deepskyblue",0,191,255,"#00bfff"),\
("dimgray",105,105,105,"#696969"),\
("dimgrey",105,105,105,"#696969"),\
("dodgerblue",30,144,255,"#1e90ff"),\
("firebrick",178,34,34,"#b22222"),\
("floralwhite",255,250,240,"#fffaf0"),\
("forestgreen",34,139,34,"#228b22"),\
("fuchsia",255,0,255,"#ff00ff"),\
("gainsboro",220,220,220,"#dcdcdc"),\
("ghostwhite",248,248,255,"#f8f8ff"),\
("gold",255,215,0,"#ffd700"),\
("goldenrod",218,165,32,"#daa520"),\
("gray",128,128,128,"#808080"),\
("green",0,128,0,"#008000"),\
("greenyellow",173,255,47,"#adff2f"),\
("grey",128,128,128,"#808080"),\
("honeydew",240,255,240,"#f0fff0"),\
("hotpink",255,105,180,"#ff69b4"),\
("indianred",205,92,92,"#cd5c5c"),\
("indigo",75,0,130,"#4b0082"),\
("ivory",255,255,240,"#fffff0"),\
("khaki",240,230,140,"#f0e68c"),\
("lavender",230,230,250,"#e6e6fa"),\
("lavenderblush",255,240,245,"#fff0f5"),\
("lawngreen",124,252,0,"#7cfc00"),\
("lemonchiffon",255,250,205,"#fffacd"),\
("lightblue",173,216,230,"#add8e6"),\
("lightcoral",240,128,128,"#f08080"),\
("lightcyan",224,255,255,"#e0ffff"),\
("lightgoldenrodyellow",250,250,210,"#fafad2"),\
("lightgray",211,211,211,"#d3d3d3"),\
("lightgreen",144,238,144,"#90ee90"),\
("lightgrey",211,211,211,"#d3d3d3"),\
("lightpink",255,182,193,"#ffb6c1"),\
("lightsalmon",255,160,122,"#ffa07a"),\
("lightseagreen",32,178,170,"#20b2aa"),\
("lightskyblue",135,206,250,"#87cefa"),\
("lightslategray",119,136,153,"#778899"),\
("lightslategrey",119,136,153,"#778899"),\
("lightsteelblue",176,196,222,"#b0c4de"),\
("lightyellow",255,255,224,"#ffffe0"),\
("lime",0,255,0,"#00ff00"),\
("limegreen",50,205,50,"#32cd32"),\
("linen",250,240,230,"#faf0e6"),\
("magenta",255,0,255,"#ff00ff"),\
("maroon",128,0,0,"#800000"),\
("mediumaquamarine",102,205,170,"#66cdaa"),\
("mediumblue",0,0,205,"#0000cd"),\
("mediumorchid",186,85,211,"#ba55d3"),\
("mediumpurple",147,112,219,"#9370db"),\
("mediumseagreen",60,179,113,"#3cb371"),\
("mediumslateblue",123,104,238,"#7b68ee"),\
("mediumspringgreen",0,250,154,"#00fa9a"),\
("mediumturquoise",72,209,204,"#48d1cc"),\
("mediumvioletred",199,21,133,"#c71585"),\
("midnightblue",25,25,112,"#191970"),\
("mintcream",245,255,250,"#f5fffa"),\
("mistyrose",255,228,225,"#ffe4e1"),\
("moccasin",255,228,181,"#ffe4b5"),\
("navajowhite",255,222,173,"#ffdead"),\
("navy",0,0,128,"#000080"),\
("oldlace",253,245,230,"#fdf5e6"),\
("olive",128,128,0,"#808000"),\
("olivedrab",107,142,35,"#6b8e23"),\
("orange",255,165,0,"#ffa500"),\
("orangered",255,69,0,"#ff4500"),\
("orchid",218,112,214,"#da70d6"),\
("palegoldenrod",238,232,170,"#eee8aa"),\
("palegreen",152,251,152,"#98fb98"),\
("paleturquoise",175,238,238,"#afeeee"),\
("palevioletred",219,112,147,"#db7093"),\
("papayawhip",255,239,213,"#ffefd5"),\
("peachpuff",255,218,185,"#ffdab9"),\
("peru",205,133,63,"#cd853f"),\
("pink",255,192,203,"#ffc0cb"),\
("plum",221,160,221,"#dda0dd"),\
("powderblue",176,224,230,"#b0e0e6"),\
("purple",128,0,128,"#800080"),\
("red",255,0,0,"#ff0000"),\
("rosybrown",188,143,143,"#bc8f8f"),\
("royalblue",65,105,225,"#4169e1"),\
("saddlebrown",139,69,19,"#8b4513"),\
("salmon",250,128,114,"#fa8072"),\
("sandybrown",244,164,96,"#f4a460"),\
("seagreen",46,139,87,"#2e8b57"),\
("seashell",255,245,238,"#fff5ee"),\
("sienna",160,82,45,"#a0522d"),\
("silver",192,192,192,"#c0c0c0"),\
("skyblue",135,206,235,"#87ceeb"),\
("slateblue",106,90,205,"#6a5acd"),\
("slategray",112,128,144,"#708090"),\
("slategrey",112,128,144,"#708090"),\
("snow",255,250,250,"#fffafa"),\
("springgreen",0,255,127,"#00ff7f"),\
("steelblue",70,130,180,"#4682b4"),\
("tan",210,180,140,"#d2b48c"),\
("teal",0,128,128,"#008080"),\
("thistle",216,191,216,"#d8bfd8"),\
("tomato",255,99,71,"#ff6347"),\
("turquoise",64,224,208,"#40e0d0"),\
("violet",238,130,238,"#ee82ee"),\
("wheat",245,222,179,"#f5deb3"),\
("white",255,255,255,"#ffffff"),\
("whitesmoke",245,245,245,"#f5f5f5"),\
("yellow",255,255,0,"#ffff00"),\
("arcafavcolor", 162,155,254,"#A29BFE"),\
("yellowgreen",154,205,50,"#9acd32")])

###################################################################

_GLI.loadKeys([
    (pygame.K_UP, ['up','up arrow']),
    (pygame.K_DOWN, ['down','down arrow']),
    (pygame.K_RIGHT, ['right','right arrow']),
    (pygame.K_LEFT, ['left','left arrow']),
    (pygame.K_BACKSPACE, ['backspace']),
    (pygame.K_SPACE, ['space', ' ']),
    (pygame.K_RETURN, ['enter', 'return']),
    (pygame.K_TAB, ['tab']),
    
    (pygame.K_a, ['a']),
    (pygame.K_b, ['b']),
    (pygame.K_c, ['c']),
    (pygame.K_d, ['d']),
    (pygame.K_e, ['e']),
    (pygame.K_f, ['f']),
    (pygame.K_g, ['g']),
    (pygame.K_h, ['h']),
    (pygame.K_i, ['i']),
    (pygame.K_j, ['j']),
    (pygame.K_k, ['k']),
    (pygame.K_l, ['l']),
    (pygame.K_m, ['m']),
    (pygame.K_n, ['n']),
    (pygame.K_o, ['o']),
    (pygame.K_p, ['p']),
    (pygame.K_q, ['q']),
    (pygame.K_r, ['r']),
    (pygame.K_s, ['s']),
    (pygame.K_t, ['t']),
    (pygame.K_u, ['u']),
    (pygame.K_v, ['v']),
    (pygame.K_w, ['w']),
    (pygame.K_x, ['x']),
    (pygame.K_y, ['y']),
    (pygame.K_z, ['z']),
    (pygame.K_0, ['0']),
    (pygame.K_1, ['1']),
    (pygame.K_2, ['2']),
    (pygame.K_3, ['3']),
    (pygame.K_4, ['4']),
    (pygame.K_5, ['5']),
    (pygame.K_6, ['6']),
    (pygame.K_7, ['7']),
    (pygame.K_8, ['8']),
    (pygame.K_9, ['9']),

    (pygame.K_BACKQUOTE, ['`' ,'backquote', 'grave', 'grave accent']),
    (pygame.K_MINUS, ['-','minus','dash','hyphen']),
    (pygame.K_EQUALS, ['=','equals']),
    (pygame.K_LEFTBRACKET, ['[','left bracket']),
    (pygame.K_RIGHTBRACKET, [']','right bracket']),
    (pygame.K_BACKSLASH, ['backslash', '\\']),
    (pygame.K_SEMICOLON, [';','semicolon']),
    (pygame.K_QUOTE, ['quote', '\'']),
    (pygame.K_COMMA, [',','comma']),
    (pygame.K_PERIOD, ['.','period']),
    (pygame.K_SLASH, ['/','slash','divide']),

    (pygame.K_DELETE, ['delete']),
    (pygame.K_INSERT, ['insert']),
    (pygame.K_HOME, ['home']),
    (pygame.K_END, ['end']),
    (pygame.K_PAGEUP, ['page up']),
    (pygame.K_PAGEDOWN, ['page down']),
    (pygame.K_CLEAR, ['clear']),
    (pygame.K_PAUSE, ['pause']),

    (pygame.K_F1, ['F1']),
    (pygame.K_F2, ['F2']),
    (pygame.K_F3, ['F3']),
    (pygame.K_F4, ['F4']),
    (pygame.K_F5, ['F5']),
    (pygame.K_F6, ['F6']),
    (pygame.K_F7, ['F7']),
    (pygame.K_F8, ['F8']),
    (pygame.K_F9, ['F9']),
    (pygame.K_F10, ['F10']),
    (pygame.K_F11, ['F11']),
    (pygame.K_F12, ['F12']),
    (pygame.K_F13, ['F13']),
    (pygame.K_F14, ['F14']),
    (pygame.K_F15, ['F15']),

    (pygame.K_RSHIFT, ['right shift']),
    (pygame.K_LSHIFT, ['left shift']),
    (pygame.K_RCTRL, ['right ctrl']),
    (pygame.K_LCTRL, ['left ctrl']),
    (pygame.K_RALT, ['right alt', 'right option']),
    (pygame.K_LALT, ['left alt', 'left option']),
    (pygame.K_RMETA, ['right command']),
    (pygame.K_LMETA, ['left command']),
    (pygame.K_LSUPER, ['left windows']),
    (pygame.K_RSUPER, ['right windows']),

    (pygame.K_NUMLOCK, ['numlock']),
    (pygame.K_CAPSLOCK, ['capslock']),
    (pygame.K_SCROLLOCK, ['scrollock']),
    (pygame.K_MODE, ['mode']),
    (pygame.K_HELP, ['help']),
    (pygame.K_PRINT, ['print','print screen','prtsc']),
    (pygame.K_SYSREQ, ['sysrq']),
    (pygame.K_BREAK, ['break']),
    (pygame.K_MENU, ['menu']),
    (pygame.K_POWER, ['power']),
    (pygame.K_EURO, ['euro']),
    
    (pygame.K_KP0, ['keypad 0']),
    (pygame.K_KP1, ['keypad 1']),
    (pygame.K_KP2, ['keypad 2']),
    (pygame.K_KP3, ['keypad 3']),
    (pygame.K_KP4, ['keypad 4']),
    (pygame.K_KP5, ['keypad 5']),
    (pygame.K_KP6, ['keypad 6']),
    (pygame.K_KP7, ['keypad 7']),
    (pygame.K_KP8, ['keypad 8']),
    (pygame.K_KP9, ['keypad 9']),
    (pygame.K_KP_PERIOD, ['keypad period']),
    (pygame.K_KP_DIVIDE, ['keypad divide']),
    (pygame.K_KP_MULTIPLY, ['keypad multiply']),
    (pygame.K_KP_MINUS, ['keypad minus']),
    (pygame.K_KP_PLUS, ['keypad plus']),
    (pygame.K_KP_EQUALS, ['keypad equals']),
    (pygame.K_KP_ENTER, ['keypad enter'])
])

###################################################################
# Backward Compatibility

addKeyDownListener = onKeyPress
addKeyUpListener = onKeyRelease
addMouseDownListener = onMousePress
addMouseUpListener = onMouseRelease
addKeyPressedListener = onKeyPress
addKeyReleasedListener = onKeyRelease
addMousePressedListener = onMousePress
addMouseReleasedListener = onMouseRelease
addWheelForwardListener = onWheelForward
addWheelBackwardListener = onWheelBackward
addMouseMotionListener = onMouseMotion
addGameControllerStickListener = onGameControllerStick
addGameControllerDPadListener = onGameControllerDPad
addGameControllerButtonPressedListener = onGameControllerButtonPress
addGameControllerButtonReleasedListener = onGameControllerButtonRelease
addTimerListener = onTimer
keyPressedNow = isKeyPressed


makeGraphicsWindow(1440,800)

 

############################################################

# this function is called once to initialize your new world

 

def startWorld(world):
    


    #everything else 
    f = open('drawingnames.json',)
    world.letters = [ ]
    world.filenames = json.load(f)
    world.loop = [ ]
    world.undoList = [ ]
    world.loadscroll = 0 
    world.screen = "main"
    world.size = 30
    world.color = "red"
    world.color1sel = [ ]
    world.color2sel = [ ]
    world.color3sel = [ ]
    world.colors = ["red","yellow", "blue","purple","black","violet","green", "arcafavcolor","lightgreen","white","orange","cyan", "pink","gray","saddlebrown"]
    world.color1 = ["red","yellow", "blue","purple","black"]
    world.color2 = ["violet","green", "arcafavcolor","lightgreen","white"]
    world.color3 = ["orange","cyan", "pink","gray","saddlebrown"]
    world.typeletters = ["q","w","e","r","t","y","u","i","o","p","a","s","d","f","g","h","j","k","l","z","x","c","v","b","n","m"]
    world.onScreen = [ f]
    for index in range(len(world.color1)):
        world.color1sel.append("black")
    for index in range(len(world.color2)):
        world.color2sel.append("black")
    for index in range(len(world.color3)):
        world.color3sel.append("black")
    world.instruction = False
    world.done = False
    world.typing = False 
    world.controlpanel = False 
    world.colornum = 0 
    world.errormsg = " "
    world.keybinds = ["Load Drawing (L)","Save Drawing (S) ","Redo (LEFT SHIFT)","Undo (Z)", "Clear Screen (DEL)","Decrease Brush Size (LEFT)", "Increase Brush Size (RIGHT)","Draw (MB1) or (SPACE)","Keybinds"]
    
############################################################

# this function is called every frame to update your world


# Python program to convert a list to string
    
# Function to convert  
def listToString(s): 
    
    # initialize an empty string
    str1 = "" 
    
    # traverse in the string  
    for ele in s: 
        str1 += ele  
    
    # return string  
    return str1 
def clickDetector(world, mouseX, mouseY, button):
    #Mouse Drawing
    if world.typing == False:
        if world.controlpanel == False:
            if world.instruction == False:
                if button == 1:  
                    if world.screen == "main": 
                        world.loop.append([getMousePosition(),world.size,world.color])
        #Load screen
        if button == 1: 
            if world.screen == "load":
                for index in range(len(world.filenames)):
                    if mouseX > getWindowWidth() / 2 - 150 and mouseX < getWindowWidth() / 2 - 150 + 300:
                        if mouseY > (index + 1) * 150 + world.loadscroll - 100 and mouseY < (index + 1) * 150 + world.loadscroll - 100 + 100:
                            print("loading")
                            f = open(world.filenames[index] + ".json",)
                            world.loop = json.load(f)
                            world.screen = "main"
                            print("loaded")
                if mouseX > 44 and mouseX < 44 + 210:
                    if mouseY >  getWindowHeight() - 44 - 44 and mouseY <  getWindowHeight() - 44 - 44 + 44:
                        world.screen = "main"
        #Color selection 1
        if button == 1: 
            if world.screen == "main":
                for index in range(len(world.color1)): 
                    if mouseX > 42 and mouseX < 42 + 42: 
                        if mouseY > 400 - 50 -84 * index and mouseY < 400 - 50 - 84 * index + 42:
                            world.color1sel = [ ]
                            world.color2sel = [ ]
                            world.color3sel = [ ]
                            for indexa in range(len(world.color1)):
                                world.color1sel.append("black")
                            for indexb in range(len(world.color2)):
                                world.color2sel.append("black")
                            for indexc in range(len(world.color3)):
                                world.color3sel.append("black")
                            world.colornum = index 
                            world.color1sel[index] = (0,200,0)
                            if world.controlpanel == False:
                                world.loop.pop(-1)
        #Color selection 2
        if button == 1: 
            if world.screen == "main":
                for index in range(len(world.color2)): 
                    if mouseX > 126 and mouseX < 126 + 42: 
                        if mouseY > 400 - 50 - 84 * index and mouseY < 400 - 50 - 84 * index + 42:
                            world.color1sel = [ ]
                            world.color2sel = [ ]
                            world.color3sel = [ ]
                            for indexa in range(len(world.color1)):
                                world.color1sel.append("black")
                            for indexb in range(len(world.color2)):
                                world.color2sel.append("black")
                            for indexc in range(len(world.color3)):
                                world.color3sel.append("black")
                            world.colornum = index + 5
                            world.color2sel[index] = (0,200,0)
                            if world.controlpanel == False:
                                world.loop.pop(-1)
        #Color selection 3
        if button == 1: 
            if world.screen == "main":
                for index in range(len(world.color3)): 
                    if mouseX > 210 and mouseX < 210 + 42: 
                        if mouseY > 400 - 50-84 * index and mouseY < 400 - 50 - 84 * index + 42:
                            world.color1sel = [ ]
                            world.color2sel = [ ]
                            world.color3sel = [ ]
                            for indexa in range(len(world.color1)):
                                world.color1sel.append("black")
                            for indexb in range(len(world.color2)):
                                world.color2sel.append("black")
                            for indexc in range(len(world.color3)):
                                world.color3sel.append("black")
                            world.colornum = index + 10 
                            world.color3sel[index] = (0,200,0)
                            if world.controlpanel == False:
                                world.loop.pop(-1)
        #Control panel on / off 
        if mouseX > 42 and mouseX < 42 + 210: 
            if mouseY > 430 and mouseY < 430 + 50:
                if world.controlpanel == False: 
                    world.controlpanel = True
                else:
                    world.controlpanel = False
        #Verifies control panel is shown
        if world.controlpanel == True:
            #Control Panel Button 1 (Save)
            if mouseX > getWindowWidth() / 2 - 210 / 2 and mouseX < getWindowWidth() / 2 - 210 / 2 + 210:
                if mouseY > 244 and mouseY < 244 + 44: 
                    world.controlpanel = False 
                    world.typing = True 
                    for index in range(1000):
                        onAnyKeyPress(saveDrawing)
                        if world.done == True:
                            break
            #Control Panel Button 2 (Load)
            if mouseX > getWindowWidth() / 2 - 210 / 2 and mouseX < getWindowWidth() / 2 - 210 / 2 + 210:
                if mouseY > 244 + 44 + 44 and mouseY < 244 + 44 + 44 + 44:
                    world.screen = "load"
            #Control Panel Button 3 (Reset Canvas)
            if mouseX > getWindowWidth() / 2 - 210 / 2 and mouseX < getWindowWidth() / 2 - 210 / 2 + 210:
                if mouseY > 244 + 44 + 44 + 44 + 44 and mouseY < 244 + 44 + 44 + 44 + 44 + 44 + 44 :
                    if world.typing == False:
                        world.loop.clear()
                        world.undoList.clear()
            #Control Panel Button 4 (Keybinds)  
            if mouseX > getWindowWidth() / 2 - 210 / 2 and mouseX < getWindowWidth() / 2 - 210 / 2 + 210: 
                if mouseY > 244 + 44 + 44 + 44 + 44 + 44 + 44 and mouseY < 244 + 44 + 44 + 44 + 44 + 44 + 44 + 44 + 44 +44:
                    world.instruction = True 
                    world.controlpanel = False 
        #Back button in keybinds menu 
        if world.instruction == True:
            if mouseX > getWindowWidth() / 2 - 210 / 2  and mouseX < getWindowWidth() / 2 - 210 / 2  + 210:
                if mouseY > getWindowHeight() / 2 - 100 + (210 / 2 + 42)  * 2 - 42 - 100 and mouseY < getWindowHeight() / 2 - 100 + (210 / 2 + 42)  * 2 - 42 - 100 + 44:
                    world.instruction = False
                    world.controlpanel = True

def saveDrawing(world,key):
    #Converts # Key value into A,B,C value
    currentkey = getKeyName(key)
    #Submission
    if currentkey == "enter":
        #Sets world.drawingname to list of inputter letters 
        world.drawingname = listToString(world.letters) 
        if world.drawingname in world.filenames: 
            world.errormsg = "Name already in use. Please pick another"
        else: 
            #Adds selected name to list
            world.filenames.append(world.drawingname)
            #Writes list to drawingnames.json 
            with open("drawingnames.json", mode='w') as f:
                json.dumps(world.filenames)
                f.write(json.dumps(world.filenames))
            #writes drawing data to unique file 
            with open(world.drawingname + ".json", mode='w') as f:
                json.dumps(world.loop)
                f.write(json.dumps(world.loop))
            
            world.done = True
            world.typing = False
    #text deletion in input screen
    elif currentkey == "backspace":
        if len(world.letters) > 0:
            world.letters.pop(-1)
            world.onScreen = listToString(world.letters) 
    #Checks if inputted key is in list of working letters
    elif currentkey in world.typeletters:
        #Adds inputted key to list
        world.letters.append(currentkey)
        #Shows list onscreen 
        world.onScreen = listToString(world.letters)
        #Resets error message to " " 
        world.errormsg = " "
    #If inputted key is not in list of working letters
    else: 
        #Sets error message
        world.errormsg = "Type only letters"
    
def updateWorld(world):
    onMousePress(clickDetector)
    #Drawing with space key
    if isKeyPressed("space"):
        if world.typing == False:
            world.loop.append([getMousePosition(),world.size,world.color])

    #Decrease Brush Size
    if isKeyPressed("left"):
        if world.typing == False:
            if world.size > 1: 
                world.size -= 1 
    #Load screen keybind
    if isKeyPressed("l"):
        if world.typing == False:
            if world.screen == "main":
                world.screen = "load"
    
    #Save screen keybind
    if isKeyPressed("s"): 
        if world.screen == "main":
            world.typing = True 
            for index in range(1000):
                onAnyKeyPress(saveDrawing)
                if world.done == True:
                    break

    #Increase brush size    
    if isKeyPressed("right"):
        if world.typing == False:
            if world.size < 125:
                world.size += 1
            else:
                world.size -= 1
    
    #Reset canvas
    if isKeyPressed("backspace"):
        if world.typing == False:
            world.loop.clear()
            world.undoList.clear()

    #Redo 
    if isKeyPressed("left shift"):
        if world.typing == False:
            if len(world.undoList) > 1:
                world.loop.append(world.undoList[-1])
                world.undoList.pop(-1)
    #Undo
    if isKeyPressed("z"):
        if world.typing == False:
            if len(world.loop) > 0: 
                world.undoList.append(world.loop[-1])
                world.loop.pop(-1)

    #Color logic        
    for index in range(len(world.colors)):
        if index == world.colornum:
            world.color=world.colors[index] 

    #Scroll up on load screen
    if isKeyPressed("up"):
        if world.screen == "load":
            if world.loadscroll < 0:
                world.loadscroll += 1

    #Load down on load screen
    if isKeyPressed("down"):
        if world.screen == "load":
                world.loadscroll -= 1
    
############################################################

# this function is called every frame to draw your world

 

def drawWorld(world): 
    #Drawing logic  
    if world.screen == "main":
        for index in range(len(world.loop)):
            fillCircle(world.loop[index][0][0], world.loop[index][0][1], color=world.loop[index][2], radius=world.loop[index][1])
        #Left side UI 
        fillRectangle(0,0,300,getWindowHeight(),(100,100,100))
        #Example brush UI
        fillCircle(150,650,world.size,world.colors[world.colornum])

    #Control panel button
    if world.screen == "main":
        fillRectangle(42, 430, 210, 50,"lightgray")
        drawRectangle(42, 430, 210, 50)
        drawString("Control Panel",300 / 2 - widthString("Control Panel") / 2, 445)
        #Control panel UI 
        if world.controlpanel == True:
            fillRectangle(getWindowWidth() / 2 - 210 / 2 - 42 ,getWindowHeight() / 2 - 200, (210 / 2 + 42) * 2 , 400,(100,100,100))
            drawRectangle(getWindowWidth() / 2 - 210 / 2 - 42 ,getWindowHeight() / 2 - 200, (210 / 2 + 42) * 2 , 400)
            
            #box1
            fillRectangle(getWindowWidth() / 2 - 210 / 2, 244, 210, 44,"lightgray")
            drawRectangle(getWindowWidth() / 2 - 210 / 2, 244, 210, 44)
            drawString("Save (S)", getWindowWidth() / 2 - widthString("Save (S)") / 2, 244 + 15)
            #box 2
            fillRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44, 210, 44, "lightgray")
            drawRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44, 210, 44)
            drawString("Load (L)", getWindowWidth() / 2 - widthString("Load (L)") / 2, 244 + 15 + 44 + 44)
            #box3
            fillRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44 + 44 + 44, 210, 44, "lightgray")
            drawRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44 + 44 + 44, 210, 44)
            drawString("Reset Canvas (DEL)", getWindowWidth() / 2 - widthString("Reset Canvas (DEL)") / 2, 244 + 15 + 44 + 44 + 44 + 44)
            #box4
            fillRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44 + 44 + 44 + 44 + 44, 210, 44, "lightgray")
            drawRectangle(getWindowWidth() / 2 - 210 / 2, 244 + 44 + 44 + 44 + 44 + 44 + 44, 210, 44)
            drawString("Keybinds (K)", getWindowWidth() / 2 - widthString("Keybinds (K)") / 2, 244 + 15 + 44 + 44 + 44 + 44 + 44 +44)
    #Keybind UI
    if world.screen == "main":
        if world.instruction == True:
            fillRectangle(getWindowWidth() / 2 - 210 / 2 - 42 ,getWindowHeight() / 2 - 100 - 100, (210 / 2 + 42) * 2 , 225 + 84 + 44,(100,100,100))
            drawRectangle(getWindowWidth() / 2 - 210 / 2 - 42 ,getWindowHeight() / 2 - 100 - 100, (210 / 2 + 42) * 2 , 225 + 84 + 44)
            fillRectangle(getWindowWidth() / 2 - 210 / 2 , getWindowHeight() / 2 - 100 + (210 / 2 + 42)  * 2 - 42 - 100, 210, 44,"lightgray") 
            drawRectangle(getWindowWidth() / 2 - 210 / 2 , getWindowHeight() / 2 - 100 + (210 / 2 + 42)  * 2 - 42 - 100, 210, 44) 
            drawString("Back", getWindowWidth() / 2 - widthString("Back") / 2, getWindowHeight() / 2 - 100 + (210 / 2 + 42)  * 2 - 42 - 100 + 13)
            for index in range(len(world.keybinds)):
                drawString(world.keybinds[index], getWindowWidth() / 2 - widthString(world.keybinds[index]) / 2 , getWindowHeight() - (index + 1) * 20 -( getWindowHeight() / 2 - 100 ) - 100,color="black") 
    #load screen     
    if world.screen == "load":
        fillRectangle(0,0, getWindowWidth(),getWindowHeight(), (100,100,100))
        if world.loadscroll > -10:
            fillPolygon([(getWindowWidth() / 2, getWindowHeight() - 10),(getWindowWidth() / 2 - 40,getWindowHeight() - 30),(getWindowWidth() / 2 + 40,getWindowHeight() - 30)], "lightgray")
            drawPolygon([(getWindowWidth() / 2, getWindowHeight() - 10),(getWindowWidth() / 2 - 40,getWindowHeight() - 30),(getWindowWidth() / 2 + 40,getWindowHeight() - 30)])
        for index in range(len(world.filenames)):
            fillRectangle(getWindowWidth() / 2 - (350 / 2), (index + 1) * 150 + world.loadscroll - 100, 350, 100,"lightgray")
            drawRectangle(getWindowWidth() / 2 - (350 / 2), (index + 1) * 150 + world.loadscroll - 100, 350, 100)
            #drawRectangle(getWindowWidth() / 2 - (350 / 2), getWindowHeight() - (index + 1) * 150 + world.loadscroll, 350, 100)
            drawString(world.filenames[index], (getWindowWidth() / 2) - (widthString(world.filenames[index]) / 2), (index + 1) * 150 - 45 - heightString(world.filenames[index]) + world.loadscroll)
            fillRectangle(44, getWindowHeight() - 44 - 44, 210, 44, "lightgray" )
            drawRectangle(44, getWindowHeight() - 44 - 44, 210, 44 )
            drawString("Back",44 + 105 - widthString("Back") / 2 , getWindowHeight() - 35 - 40)
#text input
    if world.typing == True:
        fillRectangle(getWindowWidth() / 2 - widthString("Input drawing name:") - 30 ,getWindowHeight() / 2 - 60, widthString("Input drawing name:") * 2 + 60 , 80,(100,100,100))
        drawString("Input drawing name:", getWindowWidth() / 2 - widthString("Input drawing name:") - 25,getWindowHeight() / 2 - 55, color="white")
        drawLine(getWindowWidth() / 2 - widthString("Input drawing name:") - 25 ,getWindowHeight() / 2 - 30 + 20, 400 + getWindowWidth() / 2 - widthString("Input drawing name:") - 25,getWindowHeight() / 2 - 30 + 20, "white")
        if len(world.letters) > 0:
            drawString(world.onScreen,getWindowWidth() / 2 - widthString("Input drawing name:") - 25,getWindowHeight() / 2 - 30, color="white",italic=True) 
        if len(world.errormsg) > 0: 
            drawString(world.errormsg, getWindowWidth() / 2 - widthString("Input drawing name:") - 25, getWindowHeight() / 2 - 5, color="red")
#color selection
    if world.screen == "main":
        for index in range(len(world.color1)):
            fillRectangle(42,  400 - 50 - 84 * index,42, 42,color = world.color1[index])
        for index in range(len(world.color2)):
            fillRectangle(126, 400 - 50 - 84 * index,42, 42,color = world.color2[index])
        for index in range(len(world.color3)):
            fillRectangle(210, 400 - 50 - 84 * index,42, 42,color = world.color3[index])

        for index in range(len(world.color1)):
            drawRectangle(42, 400 - 50 -84 * index,42, 42,color = world.color1sel[index])
        for index in range(len(world.color2)):
            drawRectangle(126, 400 - 50 - 84 * index,42, 42,color = world.color2sel[index])
        for index in range(len(world.color3)):
            drawRectangle(210, 400 - 50 - 84 * index,42, 42,color = world.color3sel[index])
            
    #drawLine(getWindowWidth() , getWindowHeight() / 2 , 0 , getWindowHeight() / 2 )
    #drawLine(getWindowWidth() / 2, 0 ,getWindowWidth() / 2, getWindowHeight() )
        

runGraphics(startWorld, updateWorld, drawWorld)
