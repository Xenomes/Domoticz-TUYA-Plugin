# Domoticz-TUYA-Plugin
TUYA Plugin for Domoticz home automation

Controls TUYA devices your network (mainly on/off switches and Lights). Tuya devices come in many brands and may come with different apps such as Smart Life or Jinvoo Smart, so select the matching App when configuring the plugin.

## Key Features

* Auto-detects devices on your account
* Tested with lights and switches (but should control other devices on/off)
* Cloud control only uses your user/password account with encrypted communications without requiring IP or device IDs or Keys to configure it
* Allows controlling Dimmer/RGB(WW) Colour for lights (⚠ RGBW(W) lights must be on a colour for correct detection ⚠)
* Supports scene activation

## Installation

Python version 3.4 or higher required & Domoticz version 3.9446 or greater.

To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* The plugin required Python library tuyaha and requests ```sudo pip3 install tuyaha requests```
* Run: ```git clone https://github.com/Xenomes/Domoticz-TUYA-Plugin.git```
* Restart Domoticz.

## Updating

To update:
* Upgrade the tuyaha and requests library ```sudo pip3 install tuyaha requests --upgrade```
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-TUYA directory.
* Run: ```git pull```
* Restart Domoticz.

## Configuration

Enter your username and password for your app account along with your country code (1=US/Canada, 55=Brazil, etc), keep the setting 'Data Timeout' disabled. The initial setup of your devices should be done with the app and this plugin will detect/use the same settings and automatically find/add the devices into Domoticz.

## Usage

In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "TUYA" -- configure and add the hardware there.
Devices detected are created in the 'Devices' tab, to use them you need to click the green arrow icon and 'Add' them to Domoticz.

## Change log

| Version | Information|
| ----- | ---------- |
| 1.0.15 | Update for blinds/cover |
| 1.0.14 | Change blinds/cover control for Domoticz 2022.2 |
| 1.0.13 | Disabled turn devices offline at startup |
| 1.0.12 | Fix for cover or blinds status |
| 1.0.11 | Added stop for cover or blinds |
| 1.0.10 | Added turn off for off-line devices |
| 1.0.9 | Changed scene switch type to push button |
| 1.0.8 | Added fix for 0 device detection |
| 1.0.7 | Added fix for error Tuyaapi time-out |
| 1.0.6 | Added detection for White and RGB(WW) lights |
| 1.0.5 | Fixed update time api to Domoticz from 10 min to 1 min |
| 1.0.4 | Add light device if no match found in the json |
| 1.0.3 | Update for tuyaha 0.0.8 |
| 1.0.2 | Update light support added temperature control |
| 1.0.1 | Support for SmartLife and Jinvoo Apps |
| 1.0.0 | Initial upload version |

## Note

I can only support devices or with similar functions that I have myself. Thank you for your understanding.

# Original project:

Fork from https://github.com/guino/tuyaha to make a standalone project.
