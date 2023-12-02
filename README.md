# Tilt Bluetooth monitor
Collection of scripts for my Pi Zero W Tilt Hydrometer monitor.

The three big players are stats.py, image_logo.py, and tilt_final.py

stats.py throws some stats up on the oled screen, image_logo.py displays the Tilt logo for a few seconds (because I can't figure out how to show an image, then display text in the same script and I got tired of messing with it, and finally tilt_final.py gets the status of the Tilt Sensor, and displays it to the screen. Then pushes are done to sheets.google.com and brewstat.us. Finally a countdown is shown to the next reading (600 seconds between reads).

Parts used:
(asins have changed since I built the project; double check before you buy!)

Tilt Hydrometer sensor - 
https://tilthydrometer.com/products/copy-of-tilt-floating-wireless-hydrometer-and-thermometer-for-brewing

Raspberry Pi Zero -
https://www.amazon.com/Raspberry-Pi-Zero-WH-Pre-Soldered/dp/B07W3GJTM1
I got the kit for the headers and usb accessories.

Power supply -
https://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Listed/dp/B00MARDJZ4

Display -
https://smile.amazon.com/gp/product/B01IWGXUAK/

Jumper wires -
https://smile.amazon.com/Haitronic-Multicolored-Breadboard-Arduino-raspberry/dp/B01LZF1ZSZ/

You'll also need some solder and a soldering iron for the Pi headers and the display


Guides used:

https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black
https://www.instructables.com/id/Reading-a-Tilt-Hydrometer-With-a-Raspberry-Pi/
https://www.youtube.com/watch?v=GozTgELT5bo&lc & http://raspberrypi4u.blogspot.com/2017/01/raspberry-pi-oled-i2c.html

Here it is in action:
https://youtu.be/XwExcNjErWU
