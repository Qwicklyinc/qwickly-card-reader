# Qwickly Card Reader

Send updates and regularly ping qwickly tools server. Meant to run on a Raspberry pi.

## Usage

Directory should be downloaded to **/home/pi/qwickly/**

Ideally this will be automatically started on boot but here's the command to run by hand:
```sh
sudo python3 /home/pi/qwickly/main.py
```

## Setting up the Raspberry pi
*Assuming the Raspberry pi is already equipped with an sd card with a working [Raspbian installation](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).*
*These steps also include installation of the [RASPIAUDIO sound card](https://www.raspiaudio.com/raspiaudio-aiy).*

#### 1. Deactiveate green LED light on boot
Open **/etc/rc.local**
Add the following lines above the "exit 0" line:
```sh
sudo -i
echo none >/sys/class/leds/led0/trigger
```

#### 2. Install sound software
```sh
sudo apt-get install mpg321
```

#### 3. Install raspiaudio 
*skip this step if you do not plan on using the raspiaudio sound card*
```sh
sudo wget -O - mic.raspiaudio.com | sudo bash
```
Say yes to the reboot. Once the reboot is complete:
```sh
sudo wget -O - test.raspiaudio.com | sudo bash
```
Open **Preferences -> Audio Device Settings**, make Alsa mixer the default sound output

#### 4. Add autostart file
Create the directory **/home/pi/.config/autostart/**

Create the file **/home/pi/.config/autostart/qwickly.desktop** with the following contents:
```
[Desktop Entry]
Type=Application
Name=Qwickly Card Swiper
Exec=sudo /usr/bin/python3 /home/pi/qwickly/main.py
```

#### 5. Clean up boot sequence output
Open **/boot/cmdline.txt**
Change `console=tty1` to `console=tty3`
Add the following settings. Make sure they are all on line 1.
```consoleblank=0 loglevel=3 logo.nologo quiet vt.global_cursor_default=0```

Open **/boot/config.txt**
Add this setting to the bottom of the file
```
disable_splash=1
```

#### 6. Change splash screen
Place the splash screen image in **/usr/share/plymouth/themes/pix/splash.png**
