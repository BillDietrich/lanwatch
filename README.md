# lanwatch
Report new devices that appear on LAN, and maintain an inventory of devices.

[IN PROTOTYPING STAGE; NOT DANGEROUS, BUT NOT READY FOR USE !!!]

![Do not use](http://4.bp.blogspot.com/-1lTbJMSPZaE/Tyu0eri0bOI/AAAAAAAAEP0/L6yk8jqGUwI/s1600/abnormal%2Bbrain.jpg "Do not use")

https://github.com/BillDietrich/lanwatch

---

## Basic installation

### Copy the minimal files to disk
In the GitHub repo, click the "Clone or download" button, then click the "Download ZIP" button.  Save the ZIP file to disk.
#### On Linux
Copy file lanwatch.py from the ZIP file to /usr/local/bin

#### On Windows 10
Copy files lanwatch.cmd and lanwatch.py from the ZIP file to some folder.

### Requires Python 3.3+
#### On Linux
```bash
# See what is installed
python3 --version

# If it's not installed:
# On Debian-type Linux:
sudo apt-get update
sudo apt-get install python3

# After python is installed:
pip3 install plyer
pip3 install scapy
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
```bash
sudo lanwatch.py
```

See desktop notifications.

### On Windows 10
Double-click on lanwatch.cmd file.

See notifications in "action center" at right end of system tray.

---

## Ways lanwatch can report IP address changes

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

For Linux, to see output, on command-line do
```bash
sudo journalctl | grep lanwatch
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

Then try steps in the "Testing" section, below.

#### On Windows 10
Double-click on lanwatch.cmd file.

Then try steps in the "Testing" section, below.

### Run the program automatically

#### From a Linux systemd service started at system boot time
```bash
sudo cp lanwatch.py /usr/local/bin		# you may have done this already
sudo edit /usr/local/bin/lanwatch.py		# to set gsUIChoice to "syslog".
sudo cp lanwatch.service /etc/systemd/system
```

After rebooting, on command-line do
```bash
sudo journalctl | grep lanwatch
```
Then try steps in the "Testing" section, below, and check the journal again.

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
11. lanwatch should report an IP address change, in whatever way it's configured to report.

---

## Testing
1. After lanwatch.py starts (either via command-line or service), add a new device on the LAN.

---

## Limitations
* Tested only on Linux Mint 19.3 Cinnamon with 5.3 kernel, and Windows 10 Home.
* Tested only with IPv4, not IPv6.
* On Linux, tested only with strongSwan/IPsec to Windscribe VPN.
* On Win10, tested only without VPN.
* Not tested on a LAN with no internet access.
* Requires Python 3.3 or greater.
* Can't guarantee that quick, transient device appear/disappear will be detected.

## To-Do

---

## Privacy Policy
This code doesn't collect, store, process, or transmit anyone's identity or personal information in any way.  It does not modify or transmit your system's data outside your system in any way.
