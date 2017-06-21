# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0


# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

#load image
image = Image.open('logo_bw.png').resize((128, 64), Image.ANTIALIAS).convert('1')

# Display image.
disp.image(image)
disp.display()
time.sleep(5)

