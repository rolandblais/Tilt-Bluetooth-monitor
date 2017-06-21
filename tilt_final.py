#goal:
#read tilt hydrometer
#diplay data
#pause xyz seconds (usually 600)
#repeat

#initialization stuff

import blescan
import sys
import requests
import datetime
import time
import bluetooth._bluetooth as bluez
import pygame
import os

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

padding = 2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Load font.
#font = ImageFont.load_default()
font = ImageFont.truetype('437.ttf', 8)


secDelay = 60 #pause for network to spin up, usually 60
delay = 600 #delay between spreadsheet updates, usually 600


for i in range(secDelay, 0, -1):
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        #draw.text((x, top),datetime.datetime.now().strftime('%H:%M:%S')),  font=font, fill=255)
        draw.text((x, top),"Pausing " + str(i) + "s...", font=font, fill=255)
        disp.image(image)
        disp.display()
        time.sleep(1)
        print str(i)


draw.rectangle((0,0,width,height), outline=0, fill=0)
draw.text((x, top),"Starting...",  font=font, fill=255)
disp.image(image)
disp.display()

#Assign uuid's of various colour tilt hydrometers. BLE devices like the tilt work primarily using advertisements.
#The first section of any advertisement is the universally unique identifier. Tilt uses a particular identifier based on the colour of the device
red     = 'a495bb10c5b14b44b5121370f02d74de'
green   = 'a495bb20c5b14b44b5121370f02d74de'
black   = 'a495bb30c5b14b44b5121370f02d74de'
purple  = 'a495bb40c5b14b44b5121370f02d74de'
orange  = 'a495bb50c5b14b44b5121370f02d74de'
blue    = 'a495bb60c5b14b44b5121370f02d74de'
yellow  = 'a495bb70c5b14b44b5121370f02d74de'
pink    = 'a495bb80c5b14b44b5121370f02d74de'

#The default device for bluetooth scan. If you're using a bluetooth dongle you may have to change this.
dev_id = 0

#function to calculate the number of days since epoch (used by google sheets)
#In python time.time() gives number of seconds since epoch (Jan 1 1970).
#Google Sheets datetime as a number is the number of days since the epoch except their epoch date is Jan 1 1900
def sheetsDate(date1):
        temp = datetime.datetime(1899, 12, 30)
        delta=date1-temp
        return float(delta.days) + (float(delta.seconds) / 86400)

#scan BLE advertisements until we see one matching our tilt uuid
def getdata():
        try:
                sock = bluez.hci_open_dev(dev_id)
        except:
                print "error accessing bluetooth device..."
                draw.rectangle((0,0,width,height), outline=0, fill=0)
                draw.text((x, top),"error accessing bluetooth device...",  font=font, fill=255)
                disp.image(image)
                disp.display()
                sys.exit(1)

        blescan.hci_le_set_scan_parameters(sock)
        blescan.hci_enable_le_scan(sock)

        gotData = 0
        while (gotData == 0):

                returnedList = blescan.parse_events(sock, 10)
                #lcd.message(returnedList)
                #print returnedList ###
                for beacon in returnedList: #returnedList is a list datatype of string datatypes seperated by commas (,)
                        output = beacon.split(',') #split the list into individual strings in an array
                        if output[1] == purple: #Change this to the colour of you tilt
                                tempf = float(output[2]) #convert the string for the temperature to a float type
                                gotData = 1
                                tiltTime = sheetsDate(datetime.datetime.now())
                                tiltSG = float(output[3])/1000
                                tiltTemp = tempf
                                tiltColour = 'PURPLE'
                                tiltBeer = 'test' #Change to an identifier of a particular brew

#assign values to a dictionary variable for the http POST to google sheet
        data=   {
                        'Timepoint': tiltTime,
                        'SG': tiltSG,
                        'Temp': tiltTemp,
                        'Color': tiltColour,
                        'Beer': tiltBeer,
                        'Comment': "Pi"


                        }
        blescan.hci_disable_le_scan(sock)
        return data



        while True:
                data = getdata()
                #tempf = (float(data["Temp"]) #temp in f
                tempc = (float(data["Temp"])-32)*5/9 #convert from string to float and then farenheit to celcius just for the display
                tempc = round(tempc)                    #Round of the value to 2 decimal places
                tempf = tempc*9/5+32
                tiltSG = data['SG']



def main():

        global screen
        updateSecs = delay  #time in seconds between updating the google sheet
        screenSecs = 60

        timestamp = time.time() #Set time for beginning of loop
        updateTime = timestamp + updateSecs #Set the time for the next update to google sheets
        screenTime = timestamp + screenSecs     #Set the time to put the screen to sleep

	while True:
		data = getdata()
                #tempf = (float(data["Temp"]) #temp in f
                tempc = (float(data["Temp"])-32)*5/9 #convert from string to float and then farenheit to celcius just for the display
                tempc = round(tempc)                    #Round of the value to 2 decimal places
                tempf = tempc*9/5+32
                tiltSG = data['SG']

		#Display initial data
		draw.rectangle((0,0,width,height), outline=0, fill=0)
        	draw.text((x, top),"Gravity:" + str(tiltSG),  font=font, fill=255)
        	draw.text((x, top+12),"Temp:" + str(tempf) + "f",  font=font, fill=255)
        	draw.text((x, top+24),(datetime.datetime.now().strftime('%H:%M:%S')),  font=font, fill=255)
        	disp.image(image)
        	disp.display()


		#Post initial data
		#Tilt_Data
                r = requests.post('https://script.google.com/macros/s/AKfycbx_6Q_63GFgzrKUsrQSinpfQWDW7RJZuMMFNWrR1XdIlb-oCoU/exec', data)
                #https://script.google.com/macros/s/AKfycbx_6Q_63GFgzrKUsrQSinpfQWDW7RJZuMMFNWrR1XdIlb-oCoU/exec
                print r.text
                print tiltSG
                print tempf

                #Brewometer Cloud Data
                r = requests.post('https://script.google.com/macros/s/AKfycby4CTRc7j2zmnl9zzd6FuFNV0VfCsT9-DkJmlwZ1uJg7PWW-z8/exec', data)
                #https://script.google.com/macros/s/AKfycby4CTRc7j2zmnl9zzd6FuFNV0VfCsT9-DkJmlwZ1uJg7PWW-z8/exec
                print r.text

		#Fermenator Cloud v3
                r = requests.post('https://script.google.com/macros/s/AKfycbxqflsg9YHb8UruGF7s3Qb7tOW6ypyl3KFiDuPlDQZfyoIKnNM/exec', data)
                #https://script.google.com/macros/s/AKfycbxqflsg9YHb8UruGF7s3Qb7tOW6ypyl3KFiDuPlDQZfyoIKnNM/exec
                print r.text

                #brewstat.us
                r = requests.post('https://www.brewstat.us/tilt/vw8maenmpK/log', data)
             	#https://www.brewstat.us/tilt/vw8maenmpK/log#Change this to the address of your google sheet script
                print r.text


		for i in range(delay, 0, -1):
                	draw.rectangle((0,0,width,height), outline=0, fill=0)
                	draw.text((x, top),"Gravity:" + str(tiltSG),  font=font, fill=255)
                	draw.text((x, top+12),"Temp:" + str(tempf) + "f",  font=font, fill=255)
			draw.text((x, top+24),"Update in",  font=font, fill=255)
			draw.text((x, top+36),str(i) + " seconds",  font=font, fill=255)
			draw.text((x, top+48),(datetime.datetime.now().strftime('%H:%M:%S')),  font=font, fill=255)			
                	disp.image(image)
                	disp.display()
			time.sleep(1)
			

if __name__ == "__main__": #dont run this as a module
        main()

