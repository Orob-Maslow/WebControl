
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.wiiPendantThread import WiiPendantThread
import schedule
import threading
import cwiid
import time


class WiiPendant(MakesmithInitFuncs):
 '''
    This class will start the communication thread for the wiimote Bluetooth connection
    This class relies on the setpoints in the /etc/cwiid/wminput/ folder of files that has the names of the input fi$
    'BTN_1', 'BTN_2', 'BTN_A', 'BTN_B', 'BTN_DOWN', 'BTN_HOME', 'BTN_LEFT', 'BTN_MINUS', 'BTN_PLUS', 'BTN_RIGHT', 'B$
    It also requires that the connection script with the specific bluetooth ID of the wiimote be in /home/pi/bin/
    to get the ID:
      push 1&2 buttons on wiimote
    start pi blutooth scan:
      hcitool scan
 '''
 wiiPendantRequest = ""
 wm = None
 debug = True
 th = None

 def setup(self):
    """
       try every 5 seconds to connect if the wiimote is an option
    """
    self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings", "wiiPendantPresent")
    if self.debug:
       print("scheduling connection attempt every 10 seconds")
    schedule.every(10).seconds.do(self.openConnection)
    self.data.wiiPendantConnected = False

 def connect(self, *args):
    """
        copied from serial port connect routing to being connecting  - may not be needed
    """
    if self.debug:
          print("test connect ... need to open connection")
    self.data.config.setValue("Makesmith Settings","wiiPendantPresent",str(self.data.wiiPendant))

 def openConnection(self):
    '''
       if the wiiPendantFlag in the config is True, then check if the wiiPendant is already connected
       if not connected, then set t
    '''
    self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings", "wiiPendantPresent")
    if not self.data.wiiPendantConnected:
     if self.data.wiiPendantPresent:
      if self.debug:
            print("Wii Pendant Selected")
            if self.debug:
                  print("Press 1+2 to Connect Wii controller")
            if self.th == None:
               print("Starting Thread")
               try:
                     x = WiiPendantThread()
                     x.data = self.data
                     self.th = threading.Thread(target=x.read_buttons)
                     self.th.daemon = True
                     self.th.start()
               except RuntimeError:
                     '''
                     this is a silent fail if the wiimote is not there... should set something to know that it  isn'$
                     '''
                     print ("controller not found, press 1+2 to start connection")
      else:
            self.data.ui_queue1.put("Action", "connectionStatus",{'status': 'True'})
     else:
        if self.th != None:
                self.th.join()

 def closeConnection(self):
        '''
           tell wiiPendant to shut down
        '''
        self.wiiPendantRequest = "requestToClose"

 def getConnectionStatus(self):
        '''
          get the system handle
        '''
        return self.wiiPendantRequest
