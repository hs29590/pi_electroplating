import RPi.GPIO as GPIO
from time import sleep

class ServoGripper():
    
    def __init__(self, pwmPin=2):
        self.servoGPIOPin = pwmPin;
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.servoGPIOPin, GPIO.OUT)
        self.pwm=GPIO.PWM(self.servoGPIOPin, 50)
        self.pwm.start(0);
        self.openAngle = 160;
        self.closeAngle = 50;

    def setOpenAngle(self,openangle):
        self.openAngle = openangle;

    def setCloseAngle(self,closeangle):
        self.closeAngle = closeangle;

    def SetAngle(self,angle):
        duty = angle / 18 + 2
        GPIO.output(self.servoGPIOPin, True)
        self.pwm.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(self.servoGPIOPin, False)
        self.pwm.ChangeDutyCycle(0)

    def gripperOpen(self):
        self.SetAngle(self.openAngle);

    def gripperClose(self):
        self.SetAngle(self.closeAngle);

    def __del__(self):
        self.pwm.stop();
#        GPIO.cleanup();

