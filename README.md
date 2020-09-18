# Domoticz-TUYA-Plugin
TUYA Plugin for Domoticz home automation

Controls TUYA devices your network (mainly on/off switches and Lights). Tuya devices come in many brands and may come with different apps such as Smart Life or Jinvoo Smart, so select the matching App when configuring the plugin.

## Key Features

* Auto-detects devices on your account
* Tested with lights and switches (but should control other devices on/off)
* Cloud control only uses your user/password account with encrypted communications without requiring IP or device IDs or Keys to configure it
* Allows controlling Dimmer/RGB Color for lights
* Supports scene activation

## Installation

Python version 3.4 or higher required & Domoticz version 3.9446 or greater.

To install:
* Go in your Domoticz directory using a command line and open the plugins directory.
* The plugin requierd Python library tuyaha ```pip3 install tuyaha```
* Run: ```git clone https://github.com/Xenomes/Domoticz-TUYA-Plugin.git```
* Restart Domoticz.

## Updating

To update:
* Go in your Domoticz directory using a command line and open the plugins directory then the Domoticz-TUYA directory.
* Run: ```git pull```
* Restart Domoticz.

## Alternate Install/Update:

* Simply create a directory under domoticz/plugins directory like 'TUYA' and download/copy the plugin.py file and tuyaha directory (with all its contents) into it.
* Restart Domoticz.

## Configuration

Enter your username and password for your app account along with your country code (1=US/Canada, 55=Brazil, etc). The initial setup of your devices should be done with the app and this plugin will detect/use the same settings and automatically find/add the devices into Domoticz.

## Usage

In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "TUYA" -- configure and add the hardware there.
Devices detected are created in the 'Devices' tab, to use them you need to click the green arrow icon and 'Add' them to Domoticz.

## Change log

| Version | Information|
| ----- | ---------- |
| 1.0.2 | Update light support added temperature control |
| 1.0.1 | Support for SmartLife and Jinvoo Apps |
| 1.0.0 | Initial upload version |

# Original project:

Cloned from https://github.com/guino/tuyaha to make a standalone project.
