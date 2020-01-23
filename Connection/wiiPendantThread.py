from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from DataStructures.data import Data
from Actions import actions
import cwiid
import time


class WiiPendantThread(MakesmithInitFuncs):
 '''
    This class will communicate with the wiimote, decode the button  messages and enque the desired actions.
    Inherits wm from wiiPendant ... or at least it should.
 '''

 def __init__(self):
    """
       set up the flags for interpreting the controls
    """
    self.L = [1,2,4,8]
    self.DISTANCE = [0.1,1,10,100]
    self.Z = [0.1, 0.5, 1, 5]
    self.LED_ON = 2 # default is 10 mm.  range is  = 0.1, 1, 10, 100  Z_LED = 1 # default is 1 m.  range is 0.1, 0.5, 1, 5
    self.MINUS = 0
    self.PLUS = 0
    self.TRIGGER = 0
    self.ZTRIGGER = 0
    self.CONFIRM = -10
    self.StartTiime = time.time()
    self.HOME = 0
    self.A = 0
    self.wm = None

 def rumble(self,mode=0):
  '''
     rumble shakes the wiimote when it connects, when a movement is made, or a setting is confirmed
     Inputs:  mode 0 - heartbeat, 1, shutdown or timeout, 2 sled home reset confirmed, 3 z-axis zero confirmed
  '''
  if mode == 0: # start up heartbeat = 2 quick rumbles / prompt for confirmation
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False

  if mode == 1: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False

  if mode == 2: # sled home reset
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False

  if mode >= 30: # Z-axis zero
    self.wm.rumble=True
    time.sleep(.4)
    self.wm.rumble = False

#end rumble

 def read_buttons(self):
  try:
   while True:
    time.sleep(0.2)
    #self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings", "wiiPendantPresent")
    if self.data.wiiPendantPresent == False:
          print("wii thread running, but user has disabled option, Thread alive")
          self.data.wiiPendantConnected = False
          self.wm = None
    if self.data.wiiPendantConnected == True and self.wm == None:
          self.data.wiiPendantConnected = False
          print("check wiimote battery - connection lost, thread alive")
    elif self.data.wiiPendantConnected == False and self.wm != None:
          self.wm = None
          print("connection reset, thread alive")
    if self.data.wiiPendantConnected == False and self.wm == None:
      #print("Establishing wii mote connection")
      while not self.wm:
        try:
          self.wm=cwiid.Wiimote()
          print("wiimote connection established")
          self.wm.rpt_mode = cwiid.RPT_BTN
          self.rumble(0)
          self.data.wiiPendantConnected = True
          self.wm.led = self.L[self.LED_ON]
        except RuntimeError:
          '''
            this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
          '''
          print("Connection Failed, thread should die")
          self.data.wiiPendantConnected = False
          self.wm = None
          break # does not close the thread?
    else:
      #  not using classic, this is if the remote is standing up though you hold it sideways
      if self.CONFIRM > 0:
        elapsed = 1 - (time.time() - self.startTime)
        if elapsed > 5:
          self.rumble(1)  # cancelled due to timeout
          self.CONFIRM = - 10 # go back to normal

      if (self.wm.state['buttons'] & cwiid.BTN_A):
        if self.TRIGGER == 1:
          if self.CONFIRM > 0:
            self.TRIGGER = 0
            print("Sled HOME POSITION CONFIRMED")
            self.rumble(1)
            self.data.actions.defineHome()
            #self.data.ui_queue1.put("defineHome","nowhwere", self.DISTANCE[self.LED_ON])
        elif self.ZTRIGGER == 1:
          self.ZTRIGGER = 0
          if self.CONFIRM > 0:
            print("Z PLUNGE RESET CONFIRMED")
            self.rumble(2)
            self.data.actions.defineZ0()
            #self.data.ui_queue1.put("defineZ0","nowhwere", self.DISTANCE[self.LED_ON])
        elif (self.wm.state['buttons'] & cwiid.BTN_B):
              print("Wii Remote Disconnect - thread dead")
              self.data.wiiPendantConnected = False
        else:
          self.A = 1
      else:
        self.A = 0

      if (self.wm.state['buttons'] & cwiid.BTN_1):
        if self.TRIGGER == 0:
          if (self.wm.state['buttons'] & cwiid.BTN_UP):
            print("Pendant Sled MOVE LEFT ", self.DISTANCE[self.LED_ON])
            self.rumble(1)
            self.TRIGGER = 1
            self.data.actions.move("left",self.DISTANCE[self.LED_ON])
            #self.data.ui_queue1.put("move", "left", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
            print("Pendant Sled MOVE RIGHT ", self.DISTANCE[self.LED_ON])
            self.rumble(1)
            self.TRIGGER = 1
            self.RIGHT = 0
            self.data.actions.move("right",self.DISTANCE[self.LED_ON])
            #self.data.ui_queue1.put("move", "right", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("Pendant Sled MOVE UP ", self.DISTANCE[self.LED_ON])
            self.rumble(1)
            self.TRIGGER = 1
            self.UP = 0
            self.data.actions.move("up",self.DISTANCE[self.LED_ON])
            #self.data.ui_queue1.put("move", "up", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Pendant Sled MOVE DOWN ", self.DISTANCE[self.LED_ON] )
            self.rumble(1)
            self.TRIGGER = 1
            self.DOWN = 0
            self.data.actions.move("down",self.DISTANCE[self.LED_ON])
            #self.data.ui_queue1.put("move", "down", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Pendant Sled SET NEW HOME")
            self.rumble(1)
            self.TRIGGER = 1
            self.rumble(0)
            self.CONFIRM = 500
            self.startTime = time.clock()
      else:
        self.TRIGGER = 0

      if (self.wm.state['buttons'] & cwiid.BTN_2):
        if self.ZTRIGGER == 0:
          self.TRIGGER = 0
          if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("Pendant MOVE Z UP ", self.Z[self.LED_ON])
            self.rumble(2)
            self.ZTRIGGER = 1
            self.data.actions.moveZ("raise",self.Z[self.LED_ON])
            #self.data.ui_queue1.put("moveZ", "left", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Pendant MOVE Z DOWN ", self.Z[self.LED_ON])
            self.rumble(2)
            self.ZTRIGGER = 1
            self.data.actions.moveZ("lower",self.Z[self.LED_ON])
            #self.data.ui_queue1.put("move", "left", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Pendant SET Z to 0")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.rumble(0)
            self.CONFIRM = 200
            self.startTime = time.clock()
      else:
        self.ZTRIGGER = 0
        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
          if self.HOME == 0:
            self.HOME = 1
            print ("Pendant Sled MOVE TO HOME")
            self.rumble(1)
            self.data.actions.home()
        else:
          self.HOME = 0

      if (self.wm.state['buttons'] & cwiid.BTN_MINUS):
        if self.MINUS == 0:
          self.MINUS = 1
          self.LED_ON = self.LED_ON - 1
          if self.LED_ON < 0:
            self.LED_ON = 3
          print("Sled Move Distance is ", self.DISTANCE[self.LED_ON])
          print("Z Distance is ", self.Z[self.LED_ON])
          self.wm.led = self.L[self.LED_ON]
      else:
        self.MINUS = 0

      if (self.wm.state['buttons'] & cwiid.BTN_PLUS):
        if self.PLUS == 0:
          self.PLUS = 1
          self.LED_ON = self.LED_ON + 1
          if self.LED_ON > 3:
            self.LED_ON = 0
          print("Sled Move Distance is ", self.DISTANCE[self.LED_ON])
          print("Z Distance is ", self.Z[self.LED_ON])
          self.wm.led = self.L[self.LED_ON]
      else:
        self.PLUS = 0
      #end if
    #end if not connected
   #end while
  except RuntimeError:
      '''
          this is a silent fail if the wiimote is not there... should set something to know that it  isn'$
      '''
      print (" error, connection dropped, thread dead")
      self.wm = None
      self.data.wiiThreadAlive = False               
#END class
