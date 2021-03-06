import pygame, sys, Common, TaskHandler, Configuration
import os,subprocess, RenderObject, Keys,RenderControl
from threading import Thread

class BrightnessVolume(RenderObject.RenderObject):
    config = Configuration.getConfiguration()
    

    textFont = pygame.font.Font('theme/NotoSansSymbols-Regular.ttf', 19) 
    brightSymbol = textFont.render(u"\u26ef", True, (255,255,255))
    volSymbol = Common.loadCachedImage("theme/speaker.png")

   
    showBrightness = False
    showVolume = False

    menuAlpha = 255

    currentVolumeLevel = 0
    currentBrightnessLevel = 0

    width = 200
    height = 30

    animationId = None
    

    def render(self, screen):
        if(self.showBrightness or self.showVolume):
            overlay = pygame.Surface((self.width + 4, self.height + 4),pygame.SRCALPHA)

            backgroundShadow = pygame.Surface(((self.width,self.height)),pygame.SRCALPHA)
            backgroundShadow.fill((0,0,0, 120))
            overlay.blit(backgroundShadow, (4,4))

            background = pygame.Surface((self.width,self.height),pygame.SRCALPHA)
            background.fill((137,137,137, 255))
              

            if(self.showBrightness):
                barWidth =  (self.width - 80) * self.currentBrightnessLevel / 100
          
                if(self.currentBrightnessLevel <= 5):
                    barWidth = 5  
            else:
                barWidth =  (self.width - 80) * self.currentVolumeLevel / 100
                if(self.currentVolumeLevel < 0):
                    barWidth = 1      

            bar = pygame.Surface((barWidth,10))
            bar.fill((255,255,255, 255))

            x = (self.config["screenWidth"] - self.width + 2) / 2
            background.blit(bar, (50,10))

            if(self.showBrightness):
                background.blit(self.brightSymbol, (12,-5)) 
            else:
                background.blit(self.volSymbol, (15,11))                 
            
            overlay.blit(background, (0,0)) 

            overlayCopy = overlay.convert_alpha().copy()

            overlayCopy.fill((255, 255, 255, self.menuAlpha), None, pygame.BLEND_RGBA_MULT)

            screen.blit(overlayCopy, (x,20))

    def animationCallback(self, start, target, current, finished):
        self.menuAlpha = current

        if(finished):
            self.showBrightness = False
            self.showVolume = False

        RenderControl.setDirty()    


    def handleEvents(self, events):     
        for event in events:    
            if event.type == pygame.KEYUP:         
                if event.key == Keys.DINGOO_BUTTON_BRIGHTNESS:
                    self.updateBrightness()
                if event.key == Keys.DINGOO_BUTTON_VOL_DOWN:
                   
                    self.volumeDown()
                if event.key == Keys.DINGOO_BUTTON_VOL_UP:
                    
                    self.volumeUp()         

    def volumeUp(self):
       

        self.currentVolumeLevel = self.getCurrentVolume()
        self.showVolume = True
        self.showBrightness = False

       

        self.resetAnimation()

    def volumeDown(self):
        
        self.currentVolumeLevel = self.getCurrentVolume()
        self.showVolume = True
        self.showBrightness = False

        self.resetAnimation()

    def resetAnimation(self):
        self.menuAlpha = 255
        if(self.animationId is not None):
            TaskHandler.stopAnimation(self.animationId)            

        self.animationId = TaskHandler.addAnimation(255, 20, 600, self.animationCallback, 1500)
        
        RenderControl.setDirty()
      

    def updateBrightness(self):
        self.currentBrightnessLevel = self.getCurrentBrightness()   
       
        self.showBrightness = True
        self.showVolume = False
       
        self.resetAnimation()

    
    def getCurrentBrightness(self):
        try:
            with open("/proc/jz/backlight") as f:
                bright = f.readlines()
                
               
                return int(float(str(bright[0])))
        except Exception as ex:
            print("Could not get brightness: " + str(ex))
            return 0


    def getCurrentVolume(self):
        try:
            with open("config/volume.cfg") as f:
                vol = f.readlines()
              
               
                return int(float(str(vol[0])))
        except Exception as ex:
            print("Could not get volume: " + str(ex))
            return 0

    def initVolume(self):
        if(Configuration.isOpenDinguX()):
            return
        
        if("volumeControl" in self.config["options"] and self.config["options"]["volumeControl"]):
            print("Using volume deamon")
       
            print("Setting initial volume: " + str(self.getCurrentVolume()))
            
            os.system('./setVolume ' + str(self.getCurrentVolume()))
        else:

            os.system("killall setVolume")

            print("Setting volume to " + str(self.config["options"]["defaultVolume"]))
            os.system('./setVolume ' + str(self.config["options"]["defaultVolume"]))

    def __init__(self):  

        self.initVolume()

        if(Configuration.isRetroFW()):
            self.currentBrightnessLevel = self.getCurrentBrightness()

