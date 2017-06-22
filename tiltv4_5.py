#/usr/bin/python

import blescan
import sys
import requests
import datetime
import time
import bluetooth._bluetooth as bluez
import pygame
import os

#import Adafruit_CharLCD as LCD

# Initialize the LCD using the pins
#lcd = LCD.Adafruit_CharLCDPlate()

secDelay = 0 #paus for network to spin up, usually 60
delay = 10 #delay between spreadsheet updates, usually 600

#for i in range(secDelay, 0, -1):
#        lcd.clear()
#        lcd.message(datetime.datetime.now().strftime('%H:%M:%S'))
        #lcd.message(datetime.now().strftime('%H:%M:%S'))
#        lcd.message("\n")
#        lcd.message("Pausing ")
#        lcd.message(str(i))
#        time.sleep(1)

#lcd.set_backlight(0)#off
#lcd.message("\n")
#lcd.message("Starting...")
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
#                lcd.clear()
#                lcd.message("error accessing bluetooth device...")
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

                #lcd.message("SG:"'SG'"   Temp:"'Temp\n')
                #lcd.message("Seconds until update:"'updateTime')

###Added code here for display:
                if time.time() < screenTime:            #if the screen has been on for less than screenSecs update the display
                                nextUpdate = str(int(round(updateTime - time.time())))

                                #lcd.clear()
                                #lcd.message("G:")
                                #lcd.message(str(tiltSG))
                                #lcd.message(" ")
                                #lcd.message("T:")
                                #lcd.message(str(tempf))
                                #lcd.message("\n")
                                #lcd.message(datetime.datetime.now().strftime('%H:%M:%S'))
                                #stop
                                #lcd.clear()
                                #lcd.message(str(tiltSG))
                                #lcd.message("\n")
                                #lcd.message(str(tempf))


                else:                                                   #otherwise blank the display
                                #lcd.clear()
                                #screen.fill((0,0,0))
                                #pygame.display.flip()

                        if time.time() > updateTime: #if we've reached the update time then do a POST to the google sheet and reset the updateTime
                                #Tilt_Data
                                #Change this to the address of your google sheet script
                                r = requests.post('https://script.google.com/macros/s/AKfycbx_6Q_63GFgzrKUsrQSinpfQWDW7RJZuMMFNWrR1XdIlb-oCoU/exec', data)
                                #https://script.google.com/macros/s/AKfycbx_6Q_63GFgzrKUsrQSinpfQWDW7RJZuMMFNWrR1XdIlb-oCoU/exec

                                print r.text
                                print tiltSG
                                print tempf

                                #Brewometer Cloud Data
                                #Change this to the address of your google sheet script
                                r = requests.post('https://Change.this.to.the.URL.of.your.google.sheet.script/exec', data)
                                print r.text

                                #Fermenator Cloud v3
                                #Change this to the address of your google sheet script
                                r = requests.post('https://Change.this.to.the.URL.of.your.google.sheet.script/exec', data)
                                print r.text

                                #brewstat.us
                                #Change this to the address of your google sheet script
                                r = requests.post('https://Change.this.to.the.URL.of.your.brewstat.us.log/exec', data)
                                print r.text
                                updateTime = updateTime + updateSecs
                                nextUpdate = str(int(round(updateTime - time.time())))
 #                               lcd.clear()
 #                               lcd.message("G: ")
 #                               lcd.message(str(tiltSG))
 #                               lcd.message(" ")
 #                               lcd.message("T: ")
 #                               lcd.message(str(tempf))
 #                               lcd.message("\n")
 #                               lcd.message(datetime.datetime.now().strftime('%H:%M:%S'))
                                #lcd.message(" s:")
                                #lcd.message(nextUpdate)
                                #lcd.clear

if __name__ == "__main__": #dont run this as a module
        main()
