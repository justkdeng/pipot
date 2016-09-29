#Grow.py - monitors light and moisture of a plant pot and controls grow light and solenoid valve (water) accordingly
#Authors: Dylan Scandinaro and Ke Deng
#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import datetime
import pywapi
import string


solenoidPin = 24
growLightPin = 23

#for moisture sensor
PIN_CLK = 18
PIN_DO  = 27
PIN_DI  = 22
PIN_CS  = 17

 
GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
GPIO.setup(growLightPin, GPIO.OUT)   # Set LedPin's mode is output
GPIO.setup(solenoidPin, GPIO.OUT)   # Set LedPin's mode is output

#initialize moisture sensing pins
GPIO.setup(PIN_DI,  GPIO.OUT)
GPIO.setup(PIN_DO,  GPIO.IN)
GPIO.setup(PIN_CLK, GPIO.OUT)
GPIO.setup(PIN_CS,  GPIO.OUT)

GPIO.output(growLightPin, False) # Set LedPin high(+3.3V) to off led
GPIO.output(solenoidPin, False) # Set LedPin high(+3.3V) to off led


#Gets moisture level from moisture sensor
#Returns moisture level between 0 and 255
#Adapted from code by Heinrich Hartman found at http://heinrichhartmann.com/2014/12/14/Sensor-Monitoring-with-RaspberryPi-and-Circonus.html
#on Aug 10, 2015
def getADC(channel):
    # 1. CS LOW.
        GPIO.output(PIN_CS, True)      # clear last transmission
        GPIO.output(PIN_CS, False)     # bring CS low

    # 2. Start clock
        GPIO.output(PIN_CLK, False)  # start clock low

    # 3. Input MUX address
        for i in [1,1,channel]: # start bit + mux assignment
                 if (i == 1):
                         GPIO.output(PIN_DI, True)
                 else:
                         GPIO.output(PIN_DI, False)

                 GPIO.output(PIN_CLK, True)
                 GPIO.output(PIN_CLK, False)

        # 4. read 8 ADC bits
        ad = 0
        for i in range(8):
                GPIO.output(PIN_CLK, True)
                GPIO.output(PIN_CLK, False)
                ad <<= 1 # shift bit
                if (GPIO.input(PIN_DO)):
                        ad |= 0x1 # set first bit

        # 5. reset
        GPIO.output(PIN_CS, True)

        return ad




growLightOn=False

try:
    while True:
        print "At top of while loop, time is: %s" %time.strftime("%a, %d %b %Y %H:%M")
        #If it is between 7am and 5pm, get data from NOAA; if it is not clear, turn the light on and set a flag
        extraTimeBecauseCloudy=False
        if datetime.time(07,0) < datetime.datetime.now().time() < datetime.time(17,0):
            #get the weather field from NOAA's entry for lebanon, NH
            noaa_result = string.lower(pywapi.get_weather_from_noaa('KLEB')['weather'])
            #if it is not sunny out, turn the light on
            if not(noaa_result=="fair" or noaa_result=="clear"):
                GPIO.output(growLightPin, True)  # turn on grow light
                growLightOn=True
                print "Grow light is on for the next hour because weather is cloudy"
                extraTimeBecauseCloudy=True #so that light does not get turned off because it is on outside of normal time range


        #if grow light is off and we are in the interval in which it should be on
            #then turn it on
        if growLightOn==False and datetime.time(17,0) < datetime.datetime.now().time() < datetime.time(23,0):
            GPIO.output(growLightPin, True)  # turn on grow light
            growLightOn=True
            print "Grow light is on"

        #if grow light is on and we are outside the interval in which it should be and we are not giving extra time because it's cloudy
            #then turn it off
        elif growLightOn==True and extraTimeBecauseCloudy==False and not(datetime.time(17,0) < datetime.datetime.now().time() < datetime.time(23,0)):
            GPIO.output(growLightPin, False) # turn off grow light
            print "Grow light is off"
            growLightOn=False

        moistureLevel = int(format(getADC(0)))
        print "moisture is %d" % moistureLevel
        if (moistureLevel < 150):
            print "moisture level below 150, turning solenoid on"
            GPIO.output(solenoidPin, True)
            print "solenoid on (water flowing)"
            time.sleep(3)
            GPIO.output(solenoidPin, False)
            print "solenoid off (water stopped)"

        time.sleep(3600) # 1 hour
        # time.sleep(10)

except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the flowing code will be  executed.
    GPIO.output(growLightPin, False)     # led off
    GPIO.output(solenoidPin, False)
    GPIO.cleanup()                     # Release resource








