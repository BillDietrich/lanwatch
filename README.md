# lanwatch
Report new devices that appear on LAN, and maintain an inventory of devices.

https://github.com/BillDietrich/lanwatch

---

## Basic installation

### Copy the minimal files to disk
In the GitHub repo, click the "Clone or download" button, then click the "Download ZIP" button.  Save the ZIP file to disk.
#### On Linux
Copy files lanwatch.py and lanwatch-MACVendors.csv from the ZIP file to /usr/local/bin
```bash
sudo cp lanwatch.py /usr/local/bin
sudo cp lanwatch-MACVendors.csv /usr/local/bin
```

#### On Windows 10
Copy files lanwatch.cmd and lanwatch.py and lanwatch-MACVendors.csv from the ZIP file to some folder.

### Requires Python 3.3+
#### On Linux
```bash
# See what is installed
python3 --version

# If it's not installed:
# On Debian-type Linux:
sudo apt-get update
sudo apt-get install python3
#sudo apt-get install python3-smbc
sudo apt-get install smbclient


# After python is installed:
pip3 install plyer
pip3 install scapy
pip3 install smbprotocol

sudo -H pip3 install plyer
sudo -H pip3 install scapy
sudo -H pip3 install smbprotocol
```

#### On Windows 10
Open windows command prompt: Win+X and then choose "Command Shell (as Administrator)".

Type "python -V"

If Python is not installed:

1. Go to https://www.python.org/downloads/windows/
2. Download installer (EXE).
3. Run the installer.
4. In the installer, check the checkboxes "Installer launcher for all users" and "Add Python 3 to PATH" before you click on the Install button.
5. Near end of installation, click on "Disable limit on PATH length".
6. After installer finishes, open windows command prompt (Win+X and then choose "Command Shell (as Administrator)") and type "python -V" to verify the installation.

With Python installed:

* pip install requests
* pip install pywin32
* pip install plyer
* pip install plyer

---

## Quick-start to try lanwatch: run it manually

### On Linux command-line

1. Run the application:
```bash
sudo lanwatch.py
```

2. See desktop notifications.

3. After the notifications stop (all current devices are found), kill the application and edit the /usr/local/bin/lanwatch.csv file to add information (such as host names and descriptions: e.g. ```Joe's laptop,HP Pavilion```).  The file line format is ```MAC address,network chip vendor,host name,description```.

4. Run the application again.

5. Any time a new device appears, see a notification.

Technically, you could edit the /usr/local/bin/lanwatch.csv file while the application is running.  But there is a chance that you could be editing the file when a new device appears, and the application would read and then write the same file you're editing, which would not be good.  Best to stop the application when you want to edit the /usr/local/bin/lanwatch.csv file.

The /usr/local/bin/lanwatch-MACVendors.csv file is read only when the application is started.  So it is safe for you to edit that file at any time, but changes will not be used until you stop and restart the application.  The file line format is ```First half of MAC address,network chip vendor```.

### On Windows 10

1. Double-click on lanwatch.cmd file.

2. See notifications in "action center" at right end of system tray.

3. After the notifications stop (all current devices are found), kill the application and edit the lanwatch.csv file to add information (such as host names and descriptions: e.g. ```Joe's laptop,HP Pavilion```).  The file line format is ```MAC address,network chip vendor,host name,description```.

4. Run the application again.

5. Any time a new device appears, see a notification.

---

## Ways lanwatch can report new devices

You can choose one or more of the following:

### Desktop notifications
(This is the default setting; no edit needed unless you change things later.)

Edit lanwatch.py to set gsUIChoice to "notification".

You will see notifications on the desktop or in the "action center".

### To stdout
Edit lanwatch.py to set gsUIChoice to "stdout".

You will see reports in the command-line window where you ran lanwatch.py.

### To system log
Edit lanwatch.py to set gsUIChoice to "syslog".

You will see reports in the system log:

For Linux, to see output for new devices, on command-line do
```bash
sudo journalctl | grep lanwatch.py
```
Or to see the whole list of known devices, with newest at end, do
```bash
cat /usr/local/bin/lanwatch.csv
```

For Win10, to see output, run Event Viewer application.  Look in administrative events from Applications, and look for events with Origin "lanwatch".

---

## Ways to run lanwatch

### Run the program manually
(Easiest way to start out; try this first.)

#### On Linux command-line
```bash
sudo lanwatch.py
```

#### On Windows 10
Double-click on lanwatch.cmd file.

### Run the program automatically

#### From a Linux systemd service started at system boot time
```bash
sudo cp lanwatch.py /usr/local/bin		# you may have done this already
sudo edit /usr/local/bin/lanwatch.py	# to set gsUIChoice to "syslog", and add "/usr/local/bin/" to filenames
sudo cp lanwatch.service /etc/systemd/system
sudo systemctl enable lanwatch
sudo systemctl start lanwatch
```

When desired to see if there are any new devices, on command-line do
```bash
sudo journalctl | grep lanwatch.py
```

#### From a Windows 10 task started when you log in

1. Go to Control Panel / Administrative Tools / Program Tasks.
2. In Actions (rightmost pane), click on Local Tasks / Create Basic Task.
3. Set Name of Task to "lanwatch" (not mandatory, just for clarity).
4. Set various fields.
5. For "When do you want to run the task ?" select "At start of session".
6. For "What action do you want to take for this task ?" select "Run a program".
7. For "Program or Script" select the lanwatch.cmd file.
8. Save the task.
9. The task will appear in the list of Active Tasks (bottom of middle pane).
10. Log out and back in.
11. lanwatch should report any new LAN devices, in whatever way it's configured to report.

---

## Limitations
* Tested only on Linux Mint 19.3 Cinnamon with 5.3 kernel.
* Tested only with IPv4, not IPv6.
* On Linux, tested only with strongSwan/IPsec to Windscribe VPN, and without VPN.
* Not tested on a LAN with no internet access.
* Requires Python 3.3 or greater.
* Polls every 5 minutes, so a quick, transient device appear/disappear probably won't be detected.
* Doesn't get host names automatically, except for the local machine.

## To-Do
* Desktop notifications don't work because of sudo.
* Find a way to get host names automatically.

---

## Privacy Policy
This code doesn't collect, store, process, or transmit anyone's identity or personal information in any way.  It does not modify or transmit your system's data outside your system in any way.
