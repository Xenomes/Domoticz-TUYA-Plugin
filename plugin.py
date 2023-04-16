# Domoticz TUYA Plugin
#
# Author: Wagner Oliveira (wbbo@hotmail.com)
#
# Contributed: Xenomes (xenomes@outlook.com)
#
"""
<plugin key="tuya" name="TUYA" author="Wagner Oliveira contributed Xenomes" version="1.0.15" wikilink="" externallink="https://github.com/Xenomes/Domoticz-TUYA-Plugin.git">
    <description>
        Support forum: <a href="https://www.domoticz.com/forum/viewtopic.php?f=65&amp;t=33145">https://www.domoticz.com/forum/viewtopic.php?f=65&amp;t=33145</a><br/>
        Support forum Dutch: <a href="https://contactkring.nl/phpbb/viewtopic.php?f=60&amp;t=846">https://contactkring.nl/phpbb/viewtopic.php?f=60&amp;t=846</a><br/>
        <br/>
        <h2>TUYA Plugin v.1.0.15</h2><br/>
        This plugin is meant to control TUYA devices (mainly on/off switches and LED lights). TUYA devices may come with different brands and different Apps such as Smart Life or Jinvoo Smart, so select the corresponding App you're using below.
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Auto-detection of devices on network</li>
            <li>On/Off control, state and available status display</li>
            <li>Dimmer/RGBWW Color setting for Lights</li>
            <li>Scene activation support</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>All devices that have on/off state should be supported</li>
        </ul>
        <h3>Configuration</h3>
        Just enter your username and password for the App used and everything will be detected automatically.
        Devices can be renamed in Domoticz or you can rename them in the App and remove them from Domoticz so they are detected with a new name or layout.
    </description>
    <params>
        <param field="Username" label="App Username" width="300px" required="true" default=""/>
        <param field="Password" label="App Password" width="300px" required="true" default="" password="true"/>
        <param field="Mode1" label="Country Code" width="30px" required="true" default="1"/>
        <param field="Mode2" label="App" width="150px">
            <options>
                <option label="Tuya" value="tuya" default="true" />
                <option label="Smart Life" value="smart_life"/>
                <option label="Jinvoo Smart" value="jinvoo_smart"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18" default="true" />
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""
try:
    import Domoticz
except ImportError:
    import fakeDomoticz as Domoticz
import threading
import socket
import html
import sys
import time
import tuyaha
import math
import json

class BasePlugin:
    tuya = tuyaha.TuyaApi()
    startup = True;
    devs = {}
    last_update = 0

    def __init__(self):
        self.tuya._discovery_interval = 600
        self.tuya._query_interval = 30
        self.tuya._force_discovery = True
        return

    def onStart(self):
        Domoticz.Log("Waiting 60 seconds to connect TuyaApi login error timeout")
        t = 60
        t_end = time.time() + t
        while time.time() < t_end:
            t = t - 10
            Domoticz.Log("Waiting " + str(t) + " seconds to connect TuyaApi (Tuya Plug-in)")
            time.sleep(10.0)
        Domoticz.Log("TUYA plugin started")
        if Parameters["Mode6"] != "0":
            Domoticz.Debugging(int(Parameters["Mode6"]))
            DumpConfigToLog()
        # If Mode2 is not set (previous version didn't use it), set it
        if Parameters["Mode2"] == "":
            Parameters["Mode2"] = "tuya"
        # Create/Start update thread
        self.updateThread = threading.Thread(name="TUYAUpdateThread", target=BasePlugin.handleThread, args=(self,))
        self.updateThread.start()

    def onStop(self):
        Domoticz.Debug("onStop called")
        while (threading.active_count() > 1):
            time.sleep(1.0)

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        # Find the device for the Domoticz unit number provided
        dev = None
        # For each device
        for tmpdev in self.devs:
            # If the device we want is in this WEMO, set dev for it
            if Devices[Unit].DeviceID == tmpdev.object_id():
                dev = tmpdev

        # If we didn't find it, leave (probably disconnected at this time)
        if dev == None:
            Domoticz.Error('Command for DeviceID='+Devices[Unit].DeviceID+' but device is not available.')
            return

        if not dev.available():
            Domoticz.Log('Command for DeviceID='+Devices[Unit].DeviceID+' but device is offline.')
            return

        Domoticz.Log('Sending command for DeviceID='+Devices[Unit].DeviceID)

        # Control device and update status in Domoticz
        dev_type = dev.device_type()
        if Command == 'On':
            if dev_type == 'scene':
                dev.activate()
            else:
                dev.turn_on()
            UpdateDevice(Unit, 1, 'On', not dev.available())
        elif Command == 'Off':
            if dev_type == 'scene':
                dev.activate()
            else:
                dev.turn_off()
            UpdateDevice(Unit, 0, 'Off', not dev.available())
        # elif dev_type == 'cover':
        if Command == 'Open':
            dev.open_cover()
            UpdateDevice(Unit, 1, 'Open', not dev.available())
        elif Command == 'Stop':
            dev.stop_cover()
            UpdateDevice(Unit, 0, 'Stop', not dev.available())
        elif Command == 'Close':
            dev.close_cover()
            UpdateDevice(Unit, 0, 'Close', not dev.available())
        elif Command == 'Set Color':
            # Convert RGB to Hue+Saturation
            rgb = json.loads(Hue)
            h, s = rgb_to_hs(rgb.get("r"), rgb.get("g"), rgb.get("b"))
            mode = rgb.get("m")
            t = rgb.get("t")
            Domoticz.Debug("color="+str(rgb)+" h="+str(h)+" s="+str(s))
            # If color changed
            if Devices[Unit].Color != Hue:
                if mode == 3:
                    dev.set_color( [ h*360, s*100 ] )
                    Domoticz.Debug("Set color called")
                if mode == 2:
                    temp = round(2700+((6500-2700)/255*(255-t)))
                    Domoticz.Debug("temp = " + str(temp))
                    dev.set_color_temp( temp )
                    Domoticz.Debug("Set white called")
            # If level changed
            if Devices[Unit].sValue != str(Level):
                dev.set_brightness(round(Level*2.55))
                Domoticz.Debug("Set bright called")
            # Update status of Domoticz device
            Devices[Unit].Update(nValue=1, sValue=str(Level), TimedOut=Devices[Unit].TimedOut, Color=Hue)
        elif Command == 'Set Level':
            # Set new level
            dev.set_brightness(round(Level*2.55))
            # Update status of Domoticz device
            UpdateDevice(Unit, 1 if Devices[Unit].Type == 241 else 2, str(Level), Devices[Unit].TimedOut)

        # Set last update
        self.last_update = time.time()

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        # If it hasn't been at least 1 minute since last update, skip it
        if time.time() - self.last_update < 61:
            return
        Domoticz.Debug("onHeartbeat called time="+str(time.time()))
        self.startup = False
        # Create/Start update thread
        self.updateThread = threading.Thread(name="TUYAUpdateThread", target=BasePlugin.handleThread, args=(self,))
        self.updateThread.start()

    # Separate thread looping ever 10 seconds searching for new TUYAs on network and updating their status
    def handleThread(self):
        try:
            Domoticz.Debug("in handlethread")
            # Initialize/Update devices from TUYA API
            if self.startup == True:
                self.devs = self.tuya.init(Parameters["Username"], Parameters["Password"], Parameters["Mode1"], Parameters["Mode2"])
            else:
                Domoticz.Debug("Device count: " + str(len(Devices)))
                if int(len(self.tuya.get_all_devices())) > 0:
                    self.tuya._force_discovery = True
                    time.sleep(0.5)
                    self.tuya.refresh_access_token()
                    time.sleep(0.5)
                    self.tuya.discover_devices()
                    self.devs = self.tuya.get_all_devices()

            # Set last update
            self.last_update = time.time()

            # Update devices
            for dev in self.devs:
                Domoticz.Debug( "DEV name=" + dev.name() + " state=" +str(dev.state()) + " id=" + str(dev.object_id()) + " online=" + str(dev.available()) )
                # Get unit number, if any
                unit = getUnit(dev.object_id())
                # If it's not in Domoticz already
                if unit == 0:
                    # Add it in the next available unit number
                    unit = nextUnit()
                    dev_type = dev.device_type()
                    if dev_type == "light":
                        if dev.data.get("color_mode") == 'colour' and dev.data.get("color_temp") is not None and dev.data.get("brightness") is not None:
                            # Light Color and White temperature contol
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=241, Subtype=4, Switchtype=7, DeviceID=dev.object_id()).Create()
                        elif dev.data.get("color_mode") == 'colour' and dev.data.get("color_temp") is None and dev.data.get("brightness") is not None:
                            # Light Color control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=241, Subtype=2, Switchtype=7, DeviceID=dev.object_id()).Create()
                        elif dev.data.get("color_mode") == 'colour' and dev.data.get("color_temp") is None and dev.data.get("brightness") is None:
                            # Light Color control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=241, Subtype=2, Switchtype=7, DeviceID=dev.object_id()).Create()
                        elif dev.data.get("color_mode") == 'white' and dev.data.get("color_temp") is not None and dev.data.get("brightness") is not None:
                            # Light White temperature control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=241, Subtype=8, Switchtype=7, DeviceID=dev.object_id()).Create()
                        elif dev.data.get("color_mode") == 'white' and dev.data.get("color_temp") is None and dev.data.get("brightness") is not None:
                            # Light Brightness control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=241, Subtype=3, Switchtype=7, DeviceID=dev.object_id()).Create()
                        elif dev.data.get("color_mode") is None and dev.data.get("color_temp") is None and dev.data.get("brightness") is None:
                            # Light On/Off control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=7, Image=0, DeviceID=dev.object_id()).Create()
                        else:
                            # Light On/Off control
                            Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=7, Image=0, DeviceID=dev.object_id()).Create()
                            Domoticz.Debug("No controls found for your light device!")
                    elif dev_type == "climate":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=0, Image=16, DeviceID=dev.object_id()).Create()
                    elif dev_type == "scene":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=9, Image=9, DeviceID=dev.object_id()).Create()
                    elif dev_type == "fan":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=0, Image=7, DeviceID=dev.object_id()).Create()
                    elif dev_type == "cover":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=3, DeviceID=dev.object_id()).Create()
                    elif dev_type == "lock":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=11, DeviceID=dev.object_id()).Create()
                    elif dev_type == "switch":
                        Domoticz.Device(Name=dev.name(), Unit=unit, Type=244, Subtype=73, Switchtype=0, Image=9, DeviceID=dev.object_id()).Create()

                # Update device
                if dev.state() == False:
                    UpdateDevice(unit, 0, 'Off', not dev.available())
                elif dev.state() == True:
                    UpdateDevice(unit, 1, 'On', not dev.available())
                else:
                    Domoticz.Log('DeviceID='+Devices[unit].DeviceID+' State update skiped. status = '+str(dev.state()))

                #if dev.device_type() == 'cover' and dev.state() != 'Stop':
                #    UpdateDevice(unit, 1, 'Stop', not dev.available())

                if dev.state() == True and not dev.available():
                    UpdateDevice(unit, 0, 'Off', not dev.available())
                    Domoticz.Log('DeviceID='+Devices[unit].DeviceID+' Turned off because device is offline.')

        except Exception as err:
            Domoticz.Error("handleThread: "+str(err)+' line '+format(sys.exc_info()[-1].tb_lineno))


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

# Loop thru domoticz devices and see if there's a device with matching DeviceID, if so, return unit number, otherwise return zero
def getUnit(devid):
    unit = 0
    for x in Devices:
        if Devices[x].DeviceID == devid:
            unit = x
            break
    return unit

# Find the smallest unit number available to add a device in domoticz
def nextUnit():
    unit = 1
    while unit in Devices and unit < 255:
        unit = unit + 1
    return unit

def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (Devices[Unit].TimedOut != TimedOut):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+") TimedOut="+str(TimedOut))
    return

def rgb_to_hs(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)
    h, s = high, high

    d = high - low
    s = 0 if high == 0 else d/high

    if high == low:
        h = 0.0
    else:
        h = {
            r: (g - b) / d + (6 if g < b else 0),
            g: (b - r) / d + 2,
            b: (r - g) / d + 4,
        }[high]
        h /= 6

    return h, s
