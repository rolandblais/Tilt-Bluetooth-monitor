import blescan
import sys
import requests
import datetime
import time
import bluetooth._bluetooth as bluez
import pygame
import os
import RPi.GPIO as GPIO

#Set up the GPIO pins for the push buttons
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)
GPIO.setup(27,GPIO.IN)
GPIO.add_event_detect(17, GPIO.RISING)
GPIO.add_event_detect(27, GPIO.RISING)

#Set the framebuffer device to be tht TFT
os.environ["SDL_FBDEV"] = "/dev/fb1"
#Set the display variable for the TFT
os.environ["DISPLAY"] = "0:1"
#Set the video driver to something you know works for your display
os.environ["SDL_VIDEODRIVER"] = "directfb"

#Assign uuid's of various colour tilt hydrometers. BLE devices like the tilt work primarily using advertisements. 
#The first section of any advertisement is the universally unique identifier. Tilt uses a particular identifier based on the colour of the device
red    	= 'a495bb10c5b14b44b5121370f02d74de'
green  	= 'a495bb20c5b14b44b5121370f02d74de'
black  	= 'a495bb30c5b14b44b5121370f02d74de'
purple 	= 'a495bb40c5b14b44b5121370f02d74de'
orange 	= 'a495bb50c5b14b44b5121370f02d74de'
blue   	= 'a495bb60c5b14b44b5121370f02d74de'
yellow 	= 'a495bb70c5b14b44b5121370f02d74de'
pink   	= 'a495bb80c5b14b44b5121370f02d74de'

#The default device for bluetooth scan. If you're using a bluetooth dongle you may have to change this.
dev_id = 0

#function to arrange text on a surface before updating display
def displayText(text, size, xpos, ypos, colour, clearScreen):
	if clearScreen:
		screen.fill((0, 0, 0))
	font = pygame.font.Font(None, size)
	text = font.render(text, 0, colour)
	screen.blit(text, (xpos, ypos))

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
		sys.exit(1)

	blescan.hci_le_set_scan_parameters(sock)
	blescan.hci_enable_le_scan(sock)

	gotData = 0
	while (gotData == 0):

		returnedList = blescan.parse_events(sock, 10)

		for beacon in returnedList:			#returnedList is a list datatype of string datatypes seperated by commas (,)
			output = beacon.split(',')		#split the list into individual strings in an array
			if output[1] == black:			#Change this to the colour of you tilt
				tempf = float(output[2])	#convert the string for the temperature to a float type
				#tempc = (float(output[2]) - 32)*5/9
				#tempc = round(tempc)

				gotData = 1

				tiltTime = sheetsDate(datetime.datetime.now())
				tiltSG = float(output[3])/1000
				tiltTemp = tempf
				tiltColour = 'BLACK'
				tiltBeer = 'test' 			#Change to an identifier of a particular brew

	#assign values to a dictionary variable for the http POST to google sheet
	data= 	{
			'Time': tiltTime,
			'SG': tiltSG,
			'Temp': tiltTemp,
			'Color': tiltColour,
			'Beer': tiltBeer,
			'Comment': ""
			}
	blescan.hci_disable_le_scan(sock)
	return data
		

def main():

	global screen
	pygame.init()

	size = width, height  = 128, 128 		#size of display in pixels
	black = 0, 0, 0
	updateSecs = 600 					#time in seconds between updating the google sheet
	screenSecs = 300 					#time in seconds until blanking the display

	screen = pygame.display.set_mode(size)
	pygame.mouse.set_visible(0) 			#No mouse so no need to see the pointer
	
	timestamp = time.time() 				#Set time for beginning of loop
	updateTime = timestamp + updateSecs 	#Set the time for the next update to google sheets
	screenTime = timestamp + screenSecs 	#Set the time to put the screen to sleep

	while True:
		data = getdata()
		tempc = (float(data["Temp"])-32)*5/9 #convert from string to float and then farenheit to celcius just for the display
		tempc = round(tempc) 			#Round of the value to 2 decimal places
		tiltSG = data['SG'] 

		if time.time() < screenTime: 		#if the screen has been on for less than screenSecs update the display
			nextUpdate = str(int(round(updateTime - time.time())))
			#displayText(text, size, xpos, ypos, colour, clearScreen)    
			displayText(str(tiltSG), 50, 10, 10, (0,0,200), True)
			displayText("SG", 20, 100, 30, (0,200,0), False)
			displayText(str(tempc), 30, 15, 50, (0,0,200), False)
			displayText(u"\u00B0", 30, 60, 50, (0,200,0), False)
			displayText("C", 30, 70, 50, (0,200,0), False)
			displayText("{} secs until".format(nextUpdate), 20, 5, 90, (0,0,200), False)
			displayText("next sheet update", 20, 5, 105, (0,0,200), False) 
			pygame.display.flip()
		else: 							#otherwise blank the display
			screen.fill((0,0,0))
			pygame.display.flip()
		
		if time.time() > updateTime: 		#if we've reached the update time then do a POST to the google sheet and reset the updateTime
			r = requests.post('https://Change.this.to.the.URL.of.your.google.sheet.script/exec', data)
			#print r.text
			updateTime = updateTime + updateSecs

		if (GPIO.event_detected(17)): 		#if the button is pressed then reset the screenTime so the display is updated
			screenTime = time.time() + screenSecs
		
		if (GPIO.event_detected(27)):		#if this button is pressed then exit the program and return to the primary display
			sys.exit(0)
			


if __name__ == "__main__": 				#dont run this as a module
	main()
