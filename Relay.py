import RPi.GPIO as GPIO
import time

class Relay():

    def __init__(self, pinNo):
        GPIO.setmode(GPIO.BCM)
        self.pin = pinNo;
        GPIO.setup(pinNo, GPIO.OUT);
        GPIO.output(pinNo, GPIO.LOW); #high means off

    def __del__(self):
        GPIO.output(self.pin, GPIO.LOW);
#    GPIO.cleanup();

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH);#high means on

    def off(self):
        GPIO.output(self.pin, GPIO.LOW);
