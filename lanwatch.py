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
# https://docs.python.org/3/library/csv.html





#--------------------------------------------------------------------------------------------------

# edit these to change the behavior of the app

gsIPRange = '192.168.0.0/24'

gsAccessType = 'HTTP'         # HTTP or DNS

gsUIChoice = 'stdout'   # one or more of: notification syslog stdout

gsDatabase = 'lanwatch.csv'


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
import csv

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

gsConnectionState = 'none'    # none or 'rejected by site' or connected

gsOldIPAddress = 'start'    # start or 'internal error' or 'no network connection' or connected'

gnSleep = 0

gnNextSiteIndex = 0


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

if __name__ == '__main__':

    try:
        objDatabaseFile = open(gsDatabase, "r", newline='')
    except:
        print('open "'+gsDatabase+'" failed, creating file')
        try:
            f = open(gsDatabase,"w+")
            f.close()
            print('past close')
            objDatabaseFile = open(gsDatabase, "r", newline='')
        except:
            print('create "'+gsDatabase+'" failed')
            sys.exit()

    objDatabaseReader = csv.reader(objDatabaseFile, delimiter=' ', quotechar='|')
    for row in objDatabaseReader:
        print(', '.join(row))
    objDatabaseReader = 0
    objDatabaseFile.close()

    objDatabaseFile = open(gsDatabase, "w", newline='')
    objDatabaseWriter = csv.writer(objDatabaseFile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    objDatabaseWriter.writerow([time.strftime("%H:%M:%S")] + ['78901'])
    objDatabaseWriter.writerow([time.strftime("%H:%M:%S")] + ['jklmn'])
    objDatabaseWriter = 0
    objDatabaseFile.close()
    
    while True:

        arrsMACAddress = DoARPScan()
        print('arrsMACAddress '+str(arrsMACAddress))

        for sMACAddress in arrsMACAddress:
            sVendor = get_vendor(sMACAddress)
            print('sMACAddress '+sMACAddress+' == vendor "'+sVendor+'"')
            time.sleep(1)

        ReportNewDevice('New device on LAN: zzzzzzzzzzzzzzz')

        try:

            time.sleep(15)

        except KeyboardInterrupt:
            sys.exit()


#--------------------------------------------------------------------------------------------------
