#!/usr/bin/python
 
# spi.open(0,0) - Pin arrangement is;
# Digipot mcp 4131
# Pin 1 - Pi Pin 24 - CE0, bcm 8
# Pun 2 - Pi Pin 23 - SCLK, bcm 11
# Pun 3 - Pi Pin 19 - MOSI , bcm 10
# Pun 4 - Pi Pin GND 
# Pun 5 - Pi Pin  A-end of Pot
# Pun 6 - Pi Pin  Wiper 
# Pun 7 - Pi Pin  B-end of Pot
# Pun 8 - Pi Pin  5V

import time
import RPi.GPIO as GPIO

class DigitalVoltControl():

    def __init__(self, spi_cs = 8, spi_clk = 11, spi_mosi = 10, minV=0.1, maxV=5.0):
        self.minV = minV;
        self.maxV = maxV;
        self.SPI_CS_PIN = spi_cs;
        self.SPI_CLK_PIN = spi_clk;
        self.SPI_SDISDO_PIN = spi_mosi; # mosi
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SPI_CS_PIN, GPIO.OUT)
        GPIO.setup(self.SPI_CLK_PIN, GPIO.OUT)
        GPIO.setup(self.SPI_SDISDO_PIN, GPIO.OUT)


    def set_value(self, value):
        #print "here"
        GPIO.output(self.SPI_CS_PIN, True)

        GPIO.output(self.SPI_CLK_PIN, False)
        GPIO.output(self.SPI_CS_PIN, False)

        b = '{0:016b}'.format(value)
        for x in range(0, 16):
         #   print 'x:' + str(x) + ' -> ' + str(b[x])
            GPIO.output(self.SPI_SDISDO_PIN, int(b[x]))
            GPIO.output(self.SPI_CLK_PIN, True)
            GPIO.output(self.SPI_CLK_PIN, False)

        GPIO.output(self.SPI_CS_PIN, True)
 
    def setVoltage(self,desiredV):
        if(desiredV < self.minV):
            print "Desired V is less than min V";
        elif(desiredV > self.maxV):
            print "Desired V is more than max V";
        else:
            self.set_value(int((10.8 - desiredV) / 0.084));

#    def __del__(self):
#        GPIO.cleanup();
