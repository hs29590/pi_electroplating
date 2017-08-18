#! /usr/bin/env python
import time
import sys
import serial

from DobotSerialInterface import DobotSerialInterface
#from PythonArduinoCommander import ArduinoBoard
from DigitalVoltControl import DigitalVoltControl
from Relay import Relay
from ServoGripper import ServoGripper

import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for i in ports:
    print(i[0], " -- ", i[1], " -- ", i[2]);


DobotPort = '/dev/ttyACM0'
ecRelay = Relay(18);#bcm pin for physical pin 12
pdRelay = Relay(23);#bcm for physical 16
rhRelay = Relay(24);#bcm for physical 18
gripper = ServoGripper(2);
dvc = DigitalVoltControl();


#ArduinoPort = '/dev/ttyUSB0'
#DobotPort = 'COM4'
                
if len(sys.argv) >= 2:
    DobotPort = sys.argv[1];

print "Setting Port to %s" % (DobotPort);
    
dobot_interface = DobotSerialInterface(DobotPort)

print "Opened connection"
dobot_interface.set_speed()
dobot_interface.set_playback_config()


z_up = -20
z_down = -70
RH_Voltage = 2.8;
PD_Voltage = 1.8;
EC_Voltage = 1.2;


          # X, Y, Shake_Duration
# Beakers = [ [0, 0, 0], #0 dummy beaker for numbering
            # [-77, -255, 5], #1
	    # [46, -262, 7], #2
	    # [65, -190,  5],
        # #[55, -137, 5],  #3
	    # [159, -210, 5], #4
	    # [239, -117, 5], #5
	    # [152, -30, 5], #6
	    # [267, 0, 5], #7
	    # [237, 122, 5], #8
	    # [154,216, 5], #9
	    # [56,144, 5], #10
	    # [-198, 214, 5], #11
	    # [42, 263, 5]]; #12
            
Beakers = [ [0, 0, 0],      #0 dummy beaker for numbering
            [-140, -165, 5], #1 # -135deg
            #[-112, -271, 5],  #2 #  -112.6deg
            [-95, -284, 5],  #2 #  -112.6deg
            [0, -211, 5], #3 # -90deg
            [112, -271, 5], #4 # -67.6deg
            [149, -149, 5], #5 # -45deg
            [270, -102, 5],  #6 # -22.6deg
            [210, 5, 5],    #7 # 0deg
            [271, 113, 5],  #8 # 22.4deg
            [149, 149, 5],   #9 # 45deg
            [112, 270, 5],    #10 # 67.4deg
            [-189, 223, 5], #11 # 130deg
            [-25, 209, 5]]; #12 #97deg

            
home_xyz = [215, 0, 100];
            
time.sleep(2)


def move_xy(x,y,z,duration = 2):
    dobot_interface.send_absolute_position(x, y, z, 0);  # MOVL
    time.sleep(duration);
    

def move_angles(base, rear, front, duration = 2):
    dobot_interface.send_absolute_angles(base, rear, front, 0);
    time.sleep(duration);

def interactive_run():
    a = raw_input('Enter 0 for angles, 1 for xyz, 2 to exit: ');
    while int(a) < 2: 
        print 'Current Position: ',
        print dobot_interface.current_status.position
        print 'Current angles: ',
        print dobot_interface.current_status.angles
        s = raw_input("Please enter comma separated 3 numbers: ")
        mynums = [float(i) for i in s.split(',')]
        if(len(mynums) != 3):
            print('Need exactly 3 numbers');
        else:
            print('Moving now..');
            if(int(a) == 1): # xyz-
                move_xy(mynums[0], mynums[1], mynums[2]);
                print dobot_interface.current_status.position
            else: #a == 0 - angles
                move_angles(mynums[0], mynums[1], mynums[2]);
                print dobot_interface.current_status.angles
                
        a = raw_input('Enter 0 for angles, 1 for xyz, 2 to exit: ');   
        
    return;
  
def shake(x, y, z, shakeDuration):
    t_end = time.time() + shakeDuration;
    while time.time() < t_end:
        move_xy(x, y, z + 10, 0.3);
        move_xy(x, y, z - 10, 0.3);
    
    #move_xy(x, y, z_UP, 1);
    
def up_down_beaker(id):

    print "Doing beaker %d now" % (id);
    move_xy(Beakers[id][0], Beakers[id][1], z_up);
    move_xy(Beakers[id][0], Beakers[id][1], z_down);
    
    if(id == 1):
        ecRelay.on();
#        thisBoard.startCurrentEC();
    elif(id == 8):
        pdRelay.on();
#        thisBoard.startCurrentPD();
    elif(id == 11):
        rhRelay.on();
#        thisBoard.startCurrentRH();
        
    shake(Beakers[id][0], Beakers[id][1], z_down, Beakers[id][2]); #x, y, z and shake_duration
    
 #   thisBoard.stopCurrent();
    ecRelay.off();
    pdRelay.off();
    rhRelay.off();
    #move up
    move_xy(Beakers[id][0], Beakers[id][1], z_up);
    
    #shake to drop the excess drops
    shake(Beakers[id][0], Beakers[id][1], z_up, 1);
 
#time.sleep(3);

move_xy(home_xyz[0], home_xyz[1], home_xyz[2]);

#thisBoard = ArduinoBoard(9600, ArduinoPort);
#print "Initialized Arduino Board at" + ArduinoPort + " port with 9600 BaudRate";
#time.sleep(1);
#thisBoard.gripperOpen();

gripper.gripperOpen();

#a = raw_input("Enter 0 for automatic movement, and 1 for interactive: ");

a = 0;

if(int(a) == 0):
    num = raw_input("Enter number of Jigs: ");
    num_loops = int(num);
    while(num_loops):
        num_loops = num_loops - 1;
        
        grip = '0';
        while(grip == '0'):
#            thisBoard.gripperOpen();
            gripper.gripperOpen();
            grip = raw_input("Place Jig and then Press Enter to Close Gripper..");
#            thisBoard.gripperClose();
            gripper.gripperClose();
            grip = raw_input("Press Enter to Start Process OR 0 if Jig isn't in place..");
            
        
        #1
        move_angles(-40, 30, 10);
        move_angles(-60, 30, 10);
        move_angles(-90, 30, 10);
        move_angles(-106, 30, 10);
        move_angles(-132, 30, 10);
        #interactive_run();
        dvc.setVoltage(EC_Voltage);
#        thisBoard.setVoltage(EC_Voltage);
#        print("Voltage is ", thisBoard.readVoltage());
        up_down_beaker(1);
        

        #2
        move_angles(-112, 30, 10);
#        print("Voltage is ", thisBoard.readVoltage());
        up_down_beaker(2);
        

        #3
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(-90, 30, 10);
        up_down_beaker(3);

        #4
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(-67, 30, 10);
        up_down_beaker(4);
        #interactive_run();
        
        #5
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(-45, 30, 20);
        up_down_beaker(5);

        #6
#       print("Voltage is ", thisBoard.readVoltage());
        move_angles(-25, 30, 20);    
        up_down_beaker(6);
        
        #7
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(5, 30, 20);
        up_down_beaker(7);

        #8
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(5, 30, 20);
        move_angles(25, 30, 20);
#        thisBoard.setVoltage(PD_Voltage);
        dvc.setVoltage(PD_Voltage);
        up_down_beaker(8);
        
        #9
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(45, 20, 20);
        up_down_beaker(9);
        
        #10
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(67, 20, 20);
        up_down_beaker(10);
        
        #11
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(89, 20, 20);
        move_angles(100, 20, 20);
        move_angles(120, 20, 20);
        move_angles(130, 20, 20);
#        thisBoard.setVoltage(RH_Voltage);
        dvc.setVoltage(RH_Voltage);
        up_down_beaker(11);
        
        #12
#        print("Voltage is ", thisBoard.readVoltage());
        move_angles(120, 30, 10);
        move_angles(97, 30, 10);
        up_down_beaker(12);
        
        #Home
        move_angles(60, 20, 10);
        move_angles(30, 20, 10);
        move_angles(0, 20, 10);
        move_xy(home_xyz[0], home_xyz[1], home_xyz[2]);
        
        print "%d loops remaining" % (num_loops);
            
        cc  = raw_input("Press Enter to Open Gripper...");
#        thisBoard.gripperOpen();
        gripper.gripperOpen();
        cc = raw_input("Press Enter to Continue ..");
else:
    interactive_run();
    
#cleanup    
del gripper;
del dvc;
del ecRelay;
del pdRelay;
del rhRelay;
