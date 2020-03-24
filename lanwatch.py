#!/usr/bin/env python3

#--------------------------------------------------------------------------------------------------
# lanwatch.py        Report new devices that appear on LAN, and maintain an inventory of devices.
#                   https://github.com/BillDietrich/lawatch

# If this is going to run at boot-time, put this file in the root filesystem
# (maybe in /usr/local/bin) instead of under /home, because /home may not
# be mounted or decrypted when the service starts.

# on Linux, to see if app is running in background:
#   sudo ps -ax | grep lanwatch

# Copyright Bill Dietrich 2020


# https://www.howtogeek.com/423709/how-to-see-all-devices-on-your-network-with-nmap-on-linux/
# https://itsfoss.com/how-to-find-what-devices-are-connected-to-network-in-ubuntu/
# https://itsfoss.com/nutty-network-monitoring-tool/
# https://quassy.github.io/elementary-apps/Nutty/

# turn off VPN

# python:
# https://scapy.net/
# https://github.com/secdev/scapy
# https://github.com/williamajayi/network-scanner
# https://github.com/Honeypot-R8o/ARP-Alert/blob/master/arp-alert.py


#--------------------------------------------------------------------------------------------------

# edit these to change the behavior of the app

gsIPRange = '192.168.0.0/24'

gsAccessType = 'HTTP'         # HTTP or DNS

gsUIChoice = 'stdout'   # one or more of: notification syslog stdout

gsDatabaseFilename = 'lanwatch.csv'


#--------------------------------------------------------------------------------------------------

#import subprocess
import sys
import platform
import time         # https://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
import requests
import ipaddress
import os           # https://docs.python.org/3/library/os.html
import socket
import scapy.all as scapy
import csv          # https://docs.python.org/3/library/csv.html

gbOSLinux = (platform.system() == "Linux")
gbOSWindows = (platform.system() == "Windows")

# for Linux:
if gbOSLinux:
    import syslog       # https://docs.python.org/2/library/syslog.html
    from plyer import notification      # https://plyer.readthedocs.io/en/latest/#
    # and do "pip3 install plyer"

# for Windows 10:
if gbOSWindows:
    import win32evtlogutil
    import win32evtlog
    # and do "pip install pywin32"
    from plyer import notification      # https://plyer.readthedocs.io/en/latest/#
    # and do "pip install plyer"


#--------------------------------------------------------------------------------------------------

# state variables

garrDevices = []    # each row = [MAC address, vendor, name, description]



#--------------------------------------------------------------------------------------------------
# adapted from https://github.com/williamajayi/network-scanner/blob/master/network_scanner.py

def DoARPScan():

    global gsIPRange

    arp_req = scapy.ARP(pdst=gsIPRange)    # get an arp request
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")    # Set the destination mac address
    arp_broadcast = broadcast/arp_req   # combine the broadcast and request to send to the network

    # (scapy.srp) send and respond + allow ether frame for the answered resquests
    answered = scapy.srp(arp_broadcast, timeout=1, verbose=False)[0]

    arrsMACAddress = []
    for element in answered:
        # print('element '+str(element))
        arrsMACAddress.append(element[1].hwsrc)
    
    return arrsMACAddress


#--------------------------------------------------------------------------------------------------
# adapted from https://github.com/williamajayi/network-scanner/blob/master/network_scanner.py

def get_vendor(mac_address):

    r = requests.get("https://api.macvendors.com/" + mac_address)

    if r.status_code == 200:
        return r.text
    else:
        return "Unknown vendor"


#--------------------------------------------------------------------------------------------------

def ReportNewDevice(sMsg):

    if 'stdout' in gsUIChoice:

        print(time.strftime("%H:%M:%S")+': '+sMsg)

    if 'notification' in gsUIChoice:

        # https://plyer.readthedocs.io/en/latest/#
        # https://github.com/kivy/plyer
        # no way to have notification remain permanently

        if gbOSLinux:
            # notifications appear both on desktop (briefly) and in tray
            notification.notify(title='New device on LAN', message=sMsg, app_name='lanwatch', timeout=8*60*60)

        if gbOSWindows:
            notification.notify(title='New device on LAN', message=sMsg, app_name='lanwatch', timeout=8*60*60)

    if 'syslog' in gsUIChoice:

        if gbOSLinux:
            syslog.syslog(sMsg)
            # on Linux, to see output:
            #   sudo journalctl --pager-end
            # or
            #   sudo journalctl | grep lanwatch

        if gbOSWindows:
            # https://stackoverflow.com/questions/51385195/writing-to-windows-event-log-using-win32evtlog-from-pywin32-library
            # https://www.programcreek.com/python/example/96660/win32evtlogutil.ReportEvent
            # https://docs.microsoft.com/en-us/windows/win32/eventlog/event-logging-elements
            win32evtlogutil.ReportEvent(
                                        "lanwatch",
                                        #7040,       # event ID  # https://www.rapidtables.com/convert/number/decimal-to-binary.html
                                        1610612737,  # event ID  # https://www.rapidtables.com/convert/number/decimal-to-binary.html
                                        eventCategory=1,
                                        eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                                        strings=[sMsg],
                                        data=b"")
            # https://rosettacode.org/wiki/Write_to_Windows_event_log#Python
            # on Win10, to see output:
            # run Event Viewer application.


#--------------------------------------------------------------------------------------------------

def CreateDatabase():

    global gsDatabaseFilename

    print('CreateDatabase: called')
    f = open(gsDatabaseFilename,"w+")
    f.close()


#--------------------------------------------------------------------------------------------------

def ReadDatabase():

    global gsDatabaseFilename
    global garrDevices

    garrDevices = []

    print('ReadDatabase: called')
    objDatabaseFile = open(gsDatabaseFilename, "r", newline='')
    objDatabaseReader = csv.reader(objDatabaseFile)
    for row in objDatabaseReader:
        print('ReadDatabase: got row '+str(row))
        garrDevices.append(row)
    objDatabaseReader = 0
    objDatabaseFile.close()


#--------------------------------------------------------------------------------------------------

def WriteDatabase():

    global gsDatabaseFilename
    global garrDevices

    print('WriteDatabase: called')
    objDatabaseFile = open(gsDatabaseFilename, "w", newline='')
    objDatabaseWriter = csv.writer(objDatabaseFile)
    for row in garrDevices:
        print('WriteDatabase: write row '+str(row))
        objDatabaseWriter.writerow(row)
    #objDatabaseWriter.writerow([time.strftime("%H:%M:%S")] + ['78901'])
    #objDatabaseWriter.writerow([time.strftime("%H:%M:%S")] + ['jklmn'])
    objDatabaseWriter = 0
    objDatabaseFile.close()


#--------------------------------------------------------------------------------------------------

def bIsMACAddressInDatabase(sMACAddress):

    global garrDevices

    print('IsMACAddressInDatabase: called, sMACAddress '+sMACAddress)
    for row in garrDevices:
        if (row[0] == sMACAddress):
            return True
    return False


#--------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        ReadDatabase()
    except:
        print('read "'+gsDatabaseFilename+'" failed, creating file')
        try:
            CreateDatabase()
        except:
            print('create "'+gsDatabaseFilename+'" failed')
            sys.exit()

    while True:

        arrsMACAddress = DoARPScan()
        print('arrsMACAddress '+str(arrsMACAddress))

        for sMACAddress in arrsMACAddress:
            if (not bIsMACAddressInDatabase(sMACAddress)):
                sVendor = get_vendor(sMACAddress)
                print('new sMACAddress '+sMACAddress+' == vendor "'+sVendor+'"')
                ReportNewDevice('New device on LAN: sMACAddress '+sMACAddress+' == vendor "'+sVendor+'"')
                garrDevices.append([sMACAddress, sVendor, 'name', 'description'])
                try:
                    WriteDatabase()
                except:
                    print('write "'+gsDatabaseFilename+'" failed')
                    sys.exit()
                time.sleep(1)

        try:
            time.sleep(15)
        except KeyboardInterrupt:
            sys.exit()


#--------------------------------------------------------------------------------------------------
