# Qwickly Card Reader

Send updates and regularly ping qwickly tools server. Meant to run on a Raspberry pi.

Thanks to Liz for designing the icons!

MFRC522.py and SimpleMFRC522.py taken from [clever_card_kit](https://github.com/simonmonk/clever_card_kit)

## Usage

Directory should be downloaded to **/home/pi/qwickly/**
```sh
git clone https://github.com/bartPrzybysz/qwickly-card-reader.git /home/pi/qwickly
```

Ideally this will be automatically started on boot but here's the command to run by hand:
```sh
sudo python3 /home/pi/qwickly/main.py
```

## Setting up the Raspberry pi
*Assuming the Raspberry pi is already equipped with an sd card with a working [Raspbian installation](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).*


#### 1. Install sound software
```sh
sudo apt-get install mpg321
```


#### 2. Add autostart file
Create the directory **/home/pi/.config/autostart/**

Create the file **/home/pi/.config/autostart/qwickly.desktop** with the following contents:
```
[Desktop Entry]
Type=Application
Name=Qwickly Card Swiper
Exec=sudo /usr/bin/python3 /home/pi/qwickly/main.py
```

#### 3. Clean up boot sequence output
Open **/boot/cmdline.txt**

Change `console=tty1` to `console=tty3`

Add the following settings. Make sure they are all on line 1.
```
consoleblank=0 loglevel=3 logo.nologo quiet vt.global_cursor_default=0
```

Open **/boot/config.txt**
Add this setting to the bottom of the file
```
disable_splash=1
```

#### 4. Change splash screen
Place the splash screen image in **/usr/share/plymouth/themes/pix/splash.png**


#### 5. If using RFID reader, connect the GPIO pins

|Lead color|Smartcard Reader|Raspberry Pi pin|
|----------|----------------|----------------|
|Orange|SDA|8|
|Yellow|SCK|11|
|White|MOSI|10|
|Green|MISO|9|
||IRQ|Not connected|
|Blue|GND|GND|
|Gray|RST|25|
|Red|3.3V|3.3V|
