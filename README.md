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


#### 5. Connect the RFID reader
*Skip this step if not useing the RFID reader*

Go to **Preferences -> Raspberry pi Configuration**

In the **Interfaces** tab, enable **SPI**

Disconnect the power

Connect the GPIO pins:

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

#### 6. Connect the Squid LED

*Skip this step if not using the Squid LED*

|Lead color|Raspberry Pi pin|
|----------|----------------|
|Red|4|
|Black|GND|
|Green|17|
|Blue|27|

#### 7. Install the [RASPIAUDIO sound card](https://www.raspiaudio.com/raspiaudio-aiy)

*Skip this step if not using the sound card*

```sh
sudo wget -O - mic.raspiaudio.com | sudo bash
```

Say yes to the reboot. Once the reboot is complete:

```sh
sudo wget -O - test.raspiaudio.com | sudo bash
```

Go to **Preferences -> Audio Devices Setting** then click on "Select Control" and check "Master" and "Mic".

## Remotely pushing updates

Tag the the commit you want to publish with an incremented version number.

*WARNING: Never tag the same commit twice, the updater will get confused and possibly start an infinite boot loop*

Version number examples:
- v0.2
- v0.125
- v1.1
- v1.3.21
- v2.3.4.5

This can be done on a raspberry pi:
```sh
cd /home/pi/qwickly
git tag v1.2
git push origin v1.2
```

Or using the releases page on github.

Next time a Raspberry pi reboots, it will checkout the new version.

## Configuration file

To configure the card reader, place **CARDSWIPERCONFIG.json** in the root directory of a USB flashdrive and insert it into the Raspberry Pi. If the contents of **CARDSWIPERCONFIG.json** don't precisely match the contents of the local **CONFIG.json** file, its contents will be copied and the device will reboot. No card entries should be handled while the configuration USB is connected.

Example configuration file:

```JSON
{
    "network": [
        {
            "ssid": "\"MyWiFi\"",
            "psk": "\"wifiPassword\""
        },
        {
            "ssid": "\"SchoolWiFi\"",
            "scan_ssid": "1",
            "key_mgmt": "WPA-EAP",
            "group": "CCMP TKIP",
            "eap": "PEAP",
            "identity": "\"user@university.edu\"",
            "password": "\"UserPassword\"",
            "phase1": "\"peapver=0\"",
            "phase2": "\"MSCHAPV@\""
        }
    ],
    "ping_frequency": 5,
    "volume": 69,
    "announce_session_open": true,
    "announce_session_close": true,
    "custom_idle_image": "University_logo.png",
    "custom_active_image": "",
    "version": "latest"
}
```

- **network** - list of network details to be added to [wpa_supplicant.conf](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md). Note that previous network configurations will be removed.
- **ping-frequency** - Amount of time (in seconds) to wait between server updates
- **volume** - Volume ot be set with [amixer](https://www.geeksforgeeks.org/amixer-command-in-linux-with-examples/)
- **announce_session_open** / **announce_session_close** - Wether or not a sound notification should be used on course status change
- **custom_idle_image** / **custom_active_image** - Name of the custom image with the file extension (.png). The images used should also be placed in the root directory of the configuration device
- **version** - Specify which version the updater should seek out. You can specify a version tag here "v1.2". Specify "latest" to seek the latest version and "local" to freeze automatic updates. 
