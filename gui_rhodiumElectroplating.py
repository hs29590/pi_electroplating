#! /usr/bin/env python
import time
import sys
import serial
from Tkinter import *
import ttk
import thread
#from Tkinter import ttk

from DobotSerialInterface import DobotSerialInterface
from DigitalVoltControl import DigitalVoltControl
from Relay import Relay
from ServoGripper import ServoGripper

import serial.tools.list_ports
ports = list(serial.tools.list_ports.comports())
for i in ports:
    print(i[0], " -- ", i[1], " -- ", i[2]);

root = Tk()
root.title("Rh Electroplating")
framew = 500;# root w
frameh = 200; # root h
screenw = root.winfo_screenwidth();
screenh = root.winfo_screenheight();
posx = (screenw/2) - (framew/2);
posy = (screenh/2) - (frameh/2);
root.geometry("%dx%d+%d+%d" % (framew,frameh,posx,posy))

mainframe = ttk.Frame(root, padding="10 10 30 30", height=200, width=500)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=50)
mainframe.rowconfigure(0, weight=50)
mainframe.grid_propagate(0);

s = ttk.Style()
s.configure('my.TButton', font=('Helvetica', 18))

#DobotPort = 'COM4'
DobotPort = '/dev/ttyACM0'

ecRelay = Relay(18);#bcm pin for physical pin 12
pdRelay = Relay(23);#bcm for physical 16
rhRelay = Relay(24);#bcm for physical 18
gripper = ServoGripper(2);
dvc = DigitalVoltControl();

                
if len(sys.argv) >= 2:
    DobotPort = sys.argv[1];

print ("Setting Port to %s" % (DobotPort));
    
dobot_interface = DobotSerialInterface(DobotPort)

print("Opened connection")
dobot_interface.set_speed()
dobot_interface.set_playback_config()

z_up = 60
z_down = 0
RH_Voltage = 2.8;
PD_Voltage = 1.8;
EC_Voltage = 1.2;


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

def shake(x, y, z, shakeDuration):
    t_end = time.time() + shakeDuration;
    while time.time() < t_end:
        move_xy(x, y, z + 10, 0.3);
        move_xy(x, y, z - 10, 0.3);
    
def up_down_beaker(id):

    print ("Doing beaker %d now" % (id));
    move_xy(Beakers[id][0], Beakers[id][1], z_up);
    move_xy(Beakers[id][0], Beakers[id][1], z_down);
    
    if(id == 1):
        ecRelay.on();
    elif(id == 8):
        pdRelay.on();
    elif(id == 11):
        rhRelay.on();
        
    shake(Beakers[id][0], Beakers[id][1], z_down, Beakers[id][2]); #x, y, z and shake_duration
    
    ecRelay.off();
    pdRelay.off();
    rhRelay.off();
    #move up
    move_xy(Beakers[id][0], Beakers[id][1], z_up);
    
    #shake to drop the excess drops
    shake(Beakers[id][0], Beakers[id][1], z_up, 1);
 
move_xy(home_xyz[0], home_xyz[1], home_xyz[2]);


#gripper.gripperOpen();
def gripperOpen():
    print("Inside go");
    gripper.gripperOpen();

def gripperClose():
    print("Inside gc");
    gripper.gripperClose();

def stopProcess():
    print("Inside sp");
    root.quit();
#    exit(0);

def popup():
    print("Inside po");
    toplevel = Toplevel()
    toplevel.geometry("300x75+500+500");
    label1 = Label(toplevel, text="Please make sure Robot is at Home Position", height=0, width=100)
    label1.pack(padx=5)

    def okpressed():
        toplevel.destroy();
        time.sleep(1);
        thread.start_new_thread(startProcess, ());
    
    b = Button(toplevel, text="OK", command=okpressed);
    b.pack(pady=5);


def startProcess():
#    popup();
    num_loops = 1;
    while(num_loops):
        num_loops = num_loops - 1;
        
        #1
        move_angles(-40, 30, 10);
        move_angles(-60, 30, 10);
        move_angles(-90, 30, 10);
        move_angles(-106, 30, 10);
        move_angles(-132, 30, 10);
        dvc.setVoltage(EC_Voltage);
        up_down_beaker(1);
        
        #2
        move_angles(-112, 30, 10);
        up_down_beaker(2);
        
        #3
        move_angles(-90, 30, 10);
        up_down_beaker(3);

        #4
        move_angles(-67, 30, 10);
        up_down_beaker(4);
        
        #5
        move_angles(-45, 30, 20);
        up_down_beaker(5);

        #6
        move_angles(-25, 30, 20);    
        up_down_beaker(6);
        
        #7
        move_angles(5, 30, 20);
        up_down_beaker(7);

        #8
        move_angles(5, 30, 20);
        move_angles(25, 30, 20);
        dvc.setVoltage(PD_Voltage);
        up_down_beaker(8);
        
        #9
        move_angles(45, 20, 20);
        up_down_beaker(9);
        
        #10
        move_angles(67, 20, 20);
        up_down_beaker(10);
        
        #11
        move_angles(89, 20, 20);
        move_angles(100, 20, 20);
        move_angles(120, 20, 20);
        move_angles(130, 20, 20);
        dvc.setVoltage(RH_Voltage);
        up_down_beaker(11);
        
        #12
        move_angles(120, 30, 10);
        move_angles(97, 30, 10);
        up_down_beaker(12);
        
        #Home
        move_angles(60, 20, 10);
        move_angles(30, 20, 10);
        move_angles(0, 20, 10);
        move_xy(home_xyz[0], home_xyz[1], home_xyz[2]);
        
# print "%d loops remaining" % (num_loops);
            
ttk.Button(mainframe, text="Gripper Open", style='my.TButton', command=gripperOpen, width=16).grid(column=3, row=1, sticky=W)
ttk.Button(mainframe, text="Gripper Close", style='my.TButton', command=gripperClose, width=16).grid(column=3, row=3, sticky=W)
ttk.Button(mainframe, text="Start", style='my.TButton',command=popup, width=16).grid(column=1, row=1, sticky=W)
ttk.Button(mainframe, text="Stop", style='my.TButton', command=stopProcess, width=16).grid(column=1, row=3, sticky=W)

root.mainloop()

#cleanup    
thread.exit();
del gripper;
del dvc;
del ecRelay;
del pdRelay;
del rhRelay;
