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


class DobotPlating():
    def __init__(self, dobotPort='/dev/ttyACM0'):
        ports = list(serial.tools.list_ports.comports())
        for i in ports:
            print(i[0], " -- ", i[1], " -- ", i[2]);


        #self.DobotPort = 'COM4'
        self.DobotPort = dobotPort;

        self.ecRelay = Relay(18);#bcm pin for physical pin 12
        self.pdRelay = Relay(23);#bcm for physical 16
        self.rhRelay = Relay(24);#bcm for physical 18
        self.gripper = ServoGripper(2);
        self.dvc = DigitalVoltControl();

        print ("Setting Port to %s" % (self.DobotPort));
            
        self.dobot_interface = DobotSerialInterface(self.DobotPort)

        print("Opened connection")
        self.dobot_interface.set_speed()
        self.dobot_interface.set_playback_config()

        self.z_up = 60
        self.z_down = 0
        self.RH_Voltage = 2.8;
        self.PD_Voltage = 1.8;
        self.EC_Voltage = 1.2;
        
        self.home_xyz = [215, 0, 100];
                    
        time.sleep(1)

        self.move_xy(self.home_xyz[0], self.home_xyz[1], self.home_xyz[2]);

    def move_xy(self,x,y,z,duration = 2):
        self.dobot_interface.send_absolute_position(x, y, z, 0);  #MOVL
        time.sleep(duration);
        

    def move_angles(self, base, rear, front, duration = 2):
        self.dobot_interface.send_absolute_angles(base, rear, front, 0);
        time.sleep(duration);

    def shake(self,x, y, z, shakeDuration):
        t_end = time.time() + shakeDuration;
        while time.time() < t_end:
            self.move_xy(x, y, z + 10, 0.3);
            self.move_xy(x, y, z - 10, 0.3);
        
    def up_down_beaker(self,id):

        print ("Doing beaker %d now" % (id));
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_up);
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_down);
        
        if(id == 1):
            self.ecRelay.on();
        elif(id == 8):
            self.pdRelay.on();
        elif(id == 11):
            self.rhRelay.on();
            
        self.shake(Beakers[id][0], Beakers[id][1], self.z_down, Beakers[id][2]); #x, y, z and shake_duration
        
        self.ecRelay.off();
        self.pdRelay.off();
        self.rhRelay.off();
        #move up
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_up);
        
        #shake to drop the excess drops
        self.shake(Beakers[id][0], Beakers[id][1], self.z_up, 1);
     
 
    def startProcess(self):
            
        #1
        self.move_angles(-40, 30, 10);
        self.move_angles(-60, 30, 10);
        self.move_angles(-90, 30, 10);
        self.move_angles(-106, 30, 10);
        self.move_angles(-132, 30, 10);
        self.dvc.setVoltage(self.EC_Voltage);
        self.up_down_beaker(1);
        
        #2
        self.move_angles(-112, 30, 10);
        self.up_down_beaker(2);
        
        #3
        self.move_angles(-90, 30, 10);
        self.up_down_beaker(3);

        #4
        self.move_angles(-67, 30, 10);
        self.up_down_beaker(4);
        
        #5
        self.move_angles(-45, 30, 20);
        self.up_down_beaker(5);

        #6
        self.move_angles(-25, 30, 20);    
        self.up_down_beaker(6);
        
        #7
        self.move_angles(5, 30, 20);
        self.up_down_beaker(7);

        #8
        self.move_angles(5, 30, 20);
        self.move_angles(25, 30, 20);
        self.dvc.setVoltage(self.PD_Voltage);
        self.up_down_beaker(8);
        
        #9
        self.move_angles(45, 20, 20);
        self.up_down_beaker(9);
        
        #10
        self.move_angles(67, 20, 20);
        self.up_down_beaker(10);
        
        #11
        self.move_angles(89, 20, 20);
        self.move_angles(100, 20, 20);
        self.move_angles(120, 20, 20);
        self.move_angles(130, 20, 20);
        self.dvc.setVoltage(self.RH_Voltage);
        self.up_down_beaker(11);
        
        #12
        self.move_angles(120, 30, 10);
        self.move_angles(97, 30, 10);
        self.up_down_beaker(12);
        
        #Home
        self.move_angles(60, 20, 10);
        self.move_angles(30, 20, 10);
        self.move_angles(0, 20, 10);
        self.move_xy(self.home_xyz[0], self.home_xyz[1], self.home_xyz[2]);
        print("\n DONE \n");
        
    def __del__(self):
        del self.gripper;
        del self.dvc;
        del self.ecRelay;
        del self.pdRelay;
        del self.rhRelay;
   

class PlatingGUI():
    def __init__(self):
        self.root = Tk()
        self.root.title("Rh Electroplating")
        framew = 500; # root w
        frameh = 200; # root h
        screenw = self.root.winfo_screenwidth();
        screenh = self.root.winfo_screenheight();
        posx = (screenw/2) - (framew/2);
        posy = (screenh/2) - (frameh/2);
        self.root.geometry( "%dx%d+%d+%d" % (framew,frameh,posx,posy))

        self.current_status = StringVar();
        self.current_status.set('Rh Electroplating');

        self.mainframe = ttk.Frame(self.root, padding="10 10 30 30", height=200, width=500)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=50)
        self.mainframe.rowconfigure(0, weight=50)
        self.mainframe.grid_propagate(0);

        self.buttonStyle = ttk.Style()
        self.buttonStyle.configure('my.TButton', font=('Helvetica', 18))
        
        self.l = ttk.Label(self.root, textvariable=self.current_status, font=('Helvetica',18));
        self.l.place(relx=0.35, rely=0.3, anchor='sw')

        ttk.Button(self.mainframe, text="Gripper Open", style='my.TButton', command=self.gripperOpen, width=16).grid(column=3, row=1, sticky=W)
        ttk.Button(self.mainframe, text="Gripper Close", style='my.TButton', command=self.gripperClose, width=16).grid(column=3, row=3, sticky=W)
        ttk.Button(self.mainframe, text="Start", style='my.TButton',command=self.popup, width=16).grid(column=1, row=1, sticky=W)
        ttk.Button(self.mainframe, text="Stop", style='my.TButton', command=self.stopProcess, width=16).grid(column=1, row=3, sticky=W)
   
        self.dobotPlating = DobotPlating();

    def gripperOpen(self):
#        current_status_string = 'Gripper Open';
#        self.root.update_idletasks()
        self.dobotPlating.gripper.gripperOpen();


    def gripperClose(self):
#        current_status_string = 'Gripper Close';
        self.root.update_idletasks()
        self.dobotPlating.gripper.gripperClose();

    def stopProcess(self):
        self.root.quit();

    def popup(self):
        self.toplevel = Toplevel()
        self.toplevel.geometry("300x75+500+500");
        self.label1 = Label(self.toplevel, text="BRING ROBOT TO HOME POSITION", height=0, width=100)
        self.label1.pack(padx=5)
        self.but1 = Button(self.toplevel, text="OK", command=self.okpressed);
        self.but1.pack(pady=5);

    def okpressed(self):
        self.toplevel.destroy();
#        current_status_string = 'Running Process..';
        self.root.update_idletasks()
        time.sleep(1);
        self.processThread = thread.start_new_thread(self.dobotPlating.startProcess, ());
    
    def __del__(self):
        if self.processThread is not None:
            self.processThread.exit();
        del self.dobotPlating;

gui = PlatingGUI();
gui.root.mainloop();

