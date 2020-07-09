#!/usr/bin/python3

from gpiozero import Button
from gpiozero import LED
from gpiozero import RGBLED
from signal import pause
import requests
import time
import subprocess
from subprocess import check_call
import json
import os
from os import system, name   # import only system from os 

    
class MaslowButton():
    '''
     this class runs in a separate process on the raspberry pi to communicate with GPIO buttons or possibly other devices.
     The web port number must be sent as a command line arguement so it can send and receive dat with main.py.
     This class is based on and some of the code lifted from gpioActions.py in WebControl written by madgrizzle
    '''
    runpause = 0
    flag = '0'
    Buttons = []
    LEDs = []
    index = 0
    moving = False
    homeX = 0.00
    homeY = 0.00
    sledX = 0.00
    sledY = 0.00
    minX = 0.00
    minY = 0.00
    maxX = 0.00
    maxY = 0.00
    red = 0
    green = 0
    blue = 0
    statusLED = None
    LED_Color = None
    #TODO update actionList from GPIOaction.py
    actionList = ["",
                "Spindle On",
                "Spindle Off",
                "Shutdown",
                "Stop",
                "Pause", "Play",
                "Set Home",
                "Go Home",
                "Return to Center",
                "PlayLED",
                "PauseLED",
                "StopLED",
                "Tri_LED_RED",
                "Tri_LED_GREEN",
                "Tri_LED_BLUE" ]
    
    LEDStatusList = ["Idle",
                     "At Home",
                     "Homing",
                     "Run",
                     "Sled Moving",
                     "Calibrating",
                     "Paused",
                     "Cutting",
                     "Off",
                     "Z Moving",
                     "Error"]
     
    LEDColorList = ["",
                    "Off",
                    "Red On",
                    "Red Blink",
                    "Red BlinkFast",
                    "Red BlinkSlow",
                    "Yellow On",
                    "Yellow Blink",
                    "Yellow BlinkFast",
                    "Yellow BlinkSlow",
                    "Green On",
                    "Green Blink",
                    "Green BlinkFast",
                    "Green BlinkSlow",
                    "Cyan On",
                    "Cyan Blink",
                    "Cyan BlinkFast",
                    "Cyan BlinkSlow",
                    "Blue On",
                    "Blue Blink",
                    "Blue BlinkFast",
                    "Blue BlinkSlow",
                    "Magenta On",
                    "Magenta Blink",
                    "Magenta BlinkFast",
                    "Magenta BlinkSlow",
                    "White On",
                    "White Blink",
                    "White BlinkFast",
                    "White BlinkSlow"
                    ]
    start_time = time.time()
    end_time = time.time()
    webPortInt = 5000
    
    def __init__(self):
        print("setting up buttons")
        self.getWebPort()
    
    def getpause(self):
        return self.runpause

    def setpause(self, newpause):
        self.runpause = self.newpause
        
    def getActionList(self):
        return self.actionList
    
    def getLEDStatusList(self):
        return self.LEDStatusList
    
    def getLEDColorList(self):
        return self.LEDColorList
    
    def Start(self):
        print ("start press")
        Send("gcode:playRun")
        print

    def Stop(self):
        print ("Stop press")
        Send("gcode:stopRun")
        
    def getrunPause(self):
        return(self.runpause)

    def setrunPause(self, rp:int):
        self.runpause = rp
        print("set runpause to ", str(rp))

    def runPause(self):
        self.rp = self.getrunPause()
        print ("Pause press ", str(rp))
        if (rp == 0):
            self.setrunPause(1)
            Send("gcode:pauseRun")
        else:
            self.setrunPause(0)
            Send("gcode:resumeRun")
            
    def returnHome(self):
        print ("return to center")
        Send("gcode:home")
        
    def Exit(self):
        print ("EXIT")
        #Send("system:exit")
        os._exit(0)

    def Get(self, address, command):
        #try:
            URL = "http://localhost:" + str(self.webPortInt) + "/" + str(address)
            print (URL)
            r = requests.get(URL,params = command)
            print (r.text)
            return r.json()
        #except:
            print ('error getting data, check server')
            return ('error:error')
        
    def getWebPort(self):
        try:
            cwd = os.getcwd()
            print("current working directory: ", str(cwd))
            wp = '5000'
            webPortI = 5000
            path = cwd + "/buttonconfig.json"
            openpath = ""
            if (os.path.isfile(path)):
                print("path 1 is ", path)
                openpath = path
            else:
                path = "./Services/buttonconfig.json"
                if(os.path.isfile(path)):
                    print("path 2 is ", path)
                    openpath = path
                else:
                    path = "../Services/buttonconfig.json"
                    if(os.path.isfile(path)):
                        print("path 3 is ", path)
                        openpath = path
            if (openpath != ""):
                f = open(openpath, 'r')
                wp = f.readline()
                print("value read from file: ", str(wp))
                f.close
            else:
                wp = 5000
            webPortI = int(wp.strip())
            if webPortI < 0 or webPortI > 65535:
                webPortI = 5000
            self.webPortInt = webPortI
        except:
            print ("unrecognized webport.  Defaulting to port 5000")
            webPortI = 5000
            self.webPortInt = webPortI
        # TODO  add check box to settings or gpiosettings for tricolor
        # TODo add tricolor table and logic to interpret LCD_Status flag values and drive pin selection for behavior, color, and functioni assignment. 
    def Send(self,command):
        try:
            URL = "http://localhost:" + str(self.webPortInt) + "/GPIO"
            r=requests.put(URL,command)
            print (r)
        except:
            print ('error sending command, check server')

    def Shutdown(self):
        print ("shutting down system from button press")
        check_call(['sudo', 'poweroff'])
 
    def setup(self):
        try:
            #retdata = Get("GPIO", "GPIO")
            URL = "http://localhost:" + str(self.webPortInt) + "/GPIO"
            retdata = requests.get(URL,'GPIO')
            setValues = retdata.json()
            
            #print(setValues)
            for setting in setValues:
                if setting["value"] != "":
                    pinNumber = int(setting["key"][4:])
                    setGPIOAction(pinNumber, setting["value"])
            if ((self.red != 0) and (self.blue != 0) and (self.green != 0)):
                self.Status_LED = self.RGBLED(red,green,blue)
                          
        except:
            print("error contacting web port")

    def setGPIOAction(self, pin, action):
        # first remove pin assignments if already made
        foundButton = None
        for button in self.Buttons:
            if button.pin.number == pin:
                button.pin.close()
                foundButton = button
                break
        if foundButton is not None:
            self.Buttons.remove(foundButton)

        foundLED = None
        for led in self.LEDs:
            if led[1].pin.number == pin:
                led[1].pin.close()
                foundLED = led
                break
        if foundLED is not None:
            self.LEDs.remove(foundLED)
        print (self.LEDs)
        if action[:3] == "Tri":
            self.triLED = split(action,"_")
            if self.triLED[2] == "RED":
                self.ed = pin
            elif self.triLED[2] == "GREEN":
                self.green = pin
            elif self.triLED[2] == "BLUE":
                self.blue = pin
        else:
            type, pinAction = getAction(action)
            if type == "button":
                button = Button(pin)
                button.when_pressed = pinAction
                self.Buttons.append(button)
                print("set Button ", pin, " with action: ", action)
            if type == "led":
                _led = LED(pin)
                led = (action,_led)
                self.LEDs.append(led)
                print("set LED with action: " + action)
        #pause()
    def getAction(self, action):
        #print(action)
        if action == "Stop":
            return "button", Stop
        elif action == "Pause":
            return "button", runPause
        elif action == "Play":
            return "button", Start
        elif action == "Shutdown":
            return "button", Shutdown
        elif "Return" in action:
            print("set return to center as button")
            return "button", returnHome
        else:
            return "led", None
        
    def causeAction(self, action, onoff):
        for led in self.LEDs:
            if led[0] == action:
                #print(led[1])
                if onoff == "on":
                    led[1].on()
                elif onoff == "blink":
                    led[1].blink(1,1)
                elif onoff == "BlinkFast":
                    led[1].blink(0.5,0.5)
                elif onoff == "BlinkSlow":
                    led[1].pulse(2,1)
                else:
                    led[1].off()
                #print(led[1])
            if action == "PlayLED" and onoff == "on":
                causeAction("PauseLED", "off")
                causeAction("StopLED", "off")
            if action == "PauseLED" and onoff == "on":
                causeAction("PlayLED", "on")
                causeAction("StopLED", "off")
            if action == "StopLED" and onoff == "on":
                causeAction("PauseLED", "off")
                causeAction("PlayLED", "off")

    def SetLED(self, color):
        #"Off, At Home, Homing, Sled Moving, Z Moving, Z Zero, Cutting, Paused, Idle, Error, Calibrating, Need Chain Reset "
        ''' get array values from setup
        status/action, color, type
        '''
        #get pin name
        colors = split(color,' ')
        self.Status_LED.Color = (color[0])
        if color[1] == "Blink":
            self.Status_LED.Blink(1,1,0,0,color[0],(0,0,0),n,True)
        elif color[1] == "BlinkFast":
            self.Status_LED.Blink(0.5,0.5,0,0,color[0],(0,0,0),n,True)
        elif color[1] == "BlinkSlow" or color[1] == "Pulse":
            self.Status_LED.Blink(2,2,0,0,color[0],(0,0,0),n,True)
        elif color[1] == "On":
            pass
        elif color[1] == "Off":
            self.Status_LED.off()
        elif color[1] == "":
            pass
        
if __name__ == "__main__":
    MB = MaslowButton()
    MB.setup()
    #bad_chars = "'"
    print("waiting for button press")
    #TODO - put status flag in main code and update LED's based on status and settings...
    while True:
        time.sleep (3)
        try:
            items = MB.Get('Status','stuff')
            print("received: ",items)
            if (items != None):
                if (MB.flag == "0"):
                    if(items["data"]["flag"] == "1"):
                        start_time = time.time()
                else:
                    if(items["data"]["flag"] == "0"):
                        stop_time = time.time()
                MB.flag = items["data"]["flag"]
                MB.index = items["data"]["index"]
                MB.sledX = float(items["data"]["sled_location_x"])
                MB.sledY = float(items["data"]["sled_location_y"])
                MB.sledZ = float(items["data"]["sled_location_z"])
                MB.homeX = float(items["data"]["home_location_x"])
                MB.homeY = float(items["data"]["home_location_y"])
                MB.RGB_LED = items["data"]["RGB_LED"]
                MB.LED_Status = items["data"]["LED_Status"]
                MB.LED_Color = items["data"]["LED_Color"]
                if (MB.RGB_LED == "True"):
                    MB.SetLED(MB.LED_Status,MB.LED_Color)
                else:
                    if (MB.flag == 1):
                        RGC = True
                        MB.pausedGcode = False          
                    if (MB.flag == 2):
                        MB.pausedGcode = True
                    if (MB.flag == '0'): # if 0, then stopped
                        print("stopped")
                        MB.causeAction("StopLED", "on")
                        if (MB.moving == 'True'):
                            print ("Moving")
                            MB.causeAction("PlayLED", "blink")
                        if (MB.moving == 'True'):
                            print ("zMove")
                            MB.causeAction("PlayLED", "blink")
                    elif (MB.flag == '1'):
                        print ("running")
                        MB.causeAction("PlayLED", "on")
                    elif (MB.flag == '2'):
                        print ("Paused")
                        MB.causeAction("PauseLED", "on")
        except:
        # pass
            print ("error data, data source, or routine")
            #       fail in silence
