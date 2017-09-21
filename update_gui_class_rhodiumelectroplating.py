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

global_status = "Running";
process_running = False;

Beakers = [ [0, 0, 0],      #0 dummy beaker for numbering
#            [-140, -165, 5], #1 # -135deg
            [-140, -150, 60], #1 # -135deg
            #[-112, -271, 5],  #2 #  -112.6deg
            [-95, -284, 5],  #2 #  -112.6deg
            [0, -211, 5], #3 # -90deg
            # [112, -271, 5], #4 # -67.6deg
            [119, -261, 5], #4 # -67.6deg
            #[149, -149, 5], #5 # -45deg
            [158, -139, 5], #5 # -45deg
#            [270, -102, 5],  #6 # -22.6deg
            [278, -92, 5],  #6 # -22.6deg
            [210, 5, 5],    #7 # 0deg
            [271, 113, 60],  #8 # 22.4deg
            [149, 149, 5],   #9 # 45deg
            [112, 270, 5],    #10 # 67.4deg
            [-189, 223, 60], #11 # 130deg
            [-25, 209, 5]]; #12 #97deg


class DobotPlating():
    def __init__(self, dobotPort='/dev/ttyACM0'):
        ports = list(serial.tools.list_ports.comports())
        for i in ports:
            print(i[0], " -- ", i[1], " -- ", i[2]);


        #self.DobotPort = 'COM4'
        self.DobotPort = dobotPort;

        self.ecRelay = Relay(18);#bcm pin for physical pin 12
        self.pdRelay = Relay(24);#bcm for physical 18
        self.rhRelay = Relay(23);#bcm for physical 16
        self.gripper = ServoGripper(2);
        self.dvc = DigitalVoltControl();

        print ("Setting Port to %s" % (self.DobotPort));
            
        self.dobot_interface = DobotSerialInterface(self.DobotPort)

        print("Opened connection")
        self.dobot_interface.set_speed()
        self.dobot_interface.set_playback_config()

        self.z_up = 80
        self.z_down = -65
        #self.RH_Voltage = 2.5;
        #self.PD_Voltage = 1.9;
        #self.EC_Voltage = 4.8;
        
        self.home_xyz = [215, 0, 100];
                    
        time.sleep(1)
        
        global global_status
        global_status = "Rh Electroplating";


    def move_home(self):
        self.move_xy(self.home_xyz[0], self.home_xyz[1], self.home_xyz[2], 0.3);
        

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
     
 
    def startProcess(self, EC_Voltage, PD_Voltage, RH_Voltage):
        global process_running
        process_running = True;
        global global_status
        global_status = "Step 1: EC"
        #1
        self.move_angles(-40, 30, 10);
        self.move_angles(-60, 30, 10);
        self.move_angles(-90, 30, 10);
        self.move_angles(-106, 30, 10);
        self.move_angles(-132, 30, 10);
        self.dvc.setVoltage(EC_Voltage);
        self.up_down_beaker(1);
        
        #2
        global_status = "Step 2: Dragout"
        self.move_angles(-112, 30, 10);
        self.up_down_beaker(2);
        
        #3
        global_status = "Step 3: Water"
        self.move_angles(-90, 30, 10);
        self.up_down_beaker(3);

        #4
        global_status = "Step 4: Activation"
        self.move_angles(-67, 30, 10);
        self.up_down_beaker(4);
        
        #5
        global_status = "Step 5: Water"
        self.move_angles(-45, 30, 20);
        self.up_down_beaker(5);

        #6
        global_status = "Step 6: Water"
        self.move_angles(-25, 30, 20);    
        self.up_down_beaker(6);
        
        #7
        global_status = "Step 7: Water"
        self.move_angles(5, 30, 20);
        self.up_down_beaker(7);

        #8
        global_status = "Step 8: Pd Solution"
        self.move_angles(5, 30, 20);
        self.move_angles(25, 30, 20);
        self.dvc.setVoltage(PD_Voltage);
        self.up_down_beaker(8);
        
        #9
        global_status = "Step 9: Pd Dragout"
        self.move_angles(45, 20, 20);
        self.up_down_beaker(9);
        
        #10
        global_status = "Step 10: Water"
        self.move_angles(67, 20, 20);
        self.up_down_beaker(10);
        
        #11
        global_status = "Step 11: Rh Solution"
        self.move_angles(89, 20, 20);
        self.move_angles(100, 20, 20);
        self.move_angles(120, 20, 20);
        self.move_angles(130, 20, 20);
        self.dvc.setVoltage(RH_Voltage);
        self.up_down_beaker(11);
        
        #12
        global_status = "Step 12: Rh Dragout"
        self.move_angles(120, 30, 10);
        self.move_angles(97, 30, 10);
        self.up_down_beaker(12);
        
        #Home
        self.move_angles(60, 20, 10);
        self.move_angles(30, 20, 10);
        self.move_angles(0, 20, 10);

        self.move_home()
        global_status = "Done.."
        process_running = False;
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
        
        self.readyToStart = False;
        
        framew = 550; # root w
        frameh = 300; # root h
        screenw = self.root.winfo_screenwidth();
        screenh = self.root.winfo_screenheight();
        posx = (screenw/2) - (framew/2);
        posy = (screenh/2) - (frameh/2);
        self.root.geometry( "%dx%d+%d+%d" % (framew,frameh,posx,posy))

        self.current_status = StringVar();
        self.current_status.set('Rh Electroplating');

        self.mainframe = ttk.Frame(self.root, padding="10 10 30 30", height=300, width=550)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=50)
        self.mainframe.rowconfigure(0, weight=50)
        self.mainframe.grid_propagate(0);

        self.buttonStyle = ttk.Style()
        self.buttonStyle.configure('my.TButton', font=('Helvetica', 18))
        
        self.l = ttk.Label(self.root, textvariable=self.current_status, font=('Helvetica',18));
        self.l.place(relx=0.35, rely=0.3, anchor='center')

        self.ecvar = StringVar(self.root)
        self.pdvar = StringVar(self.root)
        self.rhvar = StringVar(self.root)
        
        ecchoices = { '4.0','4.5','4.7'}
        pdchoices = { '1.5','1.8','2.0','2.2','2.5'}
        rhchoices = { '1.5','1.8','2.0','2.2','2.5'}
        
        self.ecvar.set('4.7') # set the default option
        self.pdvar.set('1.8')
        self.rhvar.set('2.5')
        
        self.ecVoltage = float(self.ecvar.get());
        self.pdVoltage = float(self.pdvar.get());
        self.rhVoltage = float(self.rhvar.get());
        
        ecpopupMenu = OptionMenu(self.mainframe, self.ecvar, *ecchoices)
        Label(self.mainframe, text="EC Voltage").grid(row = 7, column = 1, padx=5, pady=5)
        ecpopupMenu.grid(row = 8, column =1)
        
        pdpopupMenu = OptionMenu(self.mainframe, self.pdvar, *pdchoices)
        Label(self.mainframe, text="Pd Voltage").grid(row = 7, column = 2, padx=5, pady=5)
        pdpopupMenu.grid(row = 8, column =2)
        
        rhpopupMenu = OptionMenu(self.mainframe, self.rhvar, *rhchoices)
        Label(self.mainframe, text="Rh Voltage").grid(row = 7, column = 3, padx=5, pady=5)
        rhpopupMenu.grid(row = 8, column =3)
        
        # link function to change dropdown
        self.ecvar.trace('w', self.ec_change)
        self.pdvar.trace('w', self.pd_change)
        self.rhvar.trace('w', self.rh_change)


        ttk.Button(self.mainframe, text="Gripper Open", style='my.TButton', command=self.gripperOpen, width=16).grid(column=3, row=2, sticky=W)
        ttk.Button(self.mainframe, text="Gripper Close", style='my.TButton', command=self.gripperClose, width=16).grid(column=3, row=3, sticky=W)
        ttk.Button(self.mainframe, text="Start", style='my.TButton',command=self.popup, width=16).grid(column=1, row=2, sticky=W )
        ttk.Button(self.mainframe, text="Stop", style='my.TButton', command=self.stopProcess, width=16).grid(column=1, row=3, sticky=W)
  
        self.root.after(1, self.initialPopup);
        self.root.after(1000, self.updateLabel);

        self.dobotPlating = DobotPlating();

    def initialPopup(self):
        self.toplevel = Toplevel()
        self.toplevel.wm_attributes("-topmost", 1) 
        self.toplevel.geometry("300x75+500+500");
        self.label1 = Label(self.toplevel, text="BRING ROBOT TO HOME POSITION", height=0, width=100)
        self.label1.pack(padx=5)
        self.but1 = Button(self.toplevel, text="OK", command=self.okpressed);
        self.but1.pack(pady=5);
        
 
    def okpressed(self):
        self.readyToStart = True;
        self.dobotPlating.move_home();
        self.toplevel.destroy();

    def ec_change(self,*args):
        self.ecVoltage = float(self.ecvar.get());
        print( 'EC Volt set to '),
        print (self.ecVoltage)


    # on change dropdown value
    def pd_change(self,*args):
        self.pdVoltage = float(self.pdvar.get());
        print( 'Pd Volt set to '),
        print (self.pdVoltage)


    # on change dropdown value
    def rh_change(self,*args):
        self.rhVoltage = float(self.rhvar.get());
        print( 'Rh Volt set to '),
        print (self.rhVoltage)

    
    def updateLabel(self):
        global global_status;
        self.current_status.set(global_status);
        self.l.config(textvariable=self.current_status);
        self.l.place(x=90, y=5)
        self.l.update_idletasks();
        self.root.update_idletasks();
        self.root.after(500, self.updateLabel);

    def gripperOpen(self):
        global process_running
        if(not process_running and self.readyToStart):
            global global_status;  
            global_status = "Gripper Open";
            self.dobotPlating.gripper.gripperOpen();


    def gripperClose(self):
        global process_running
        if(not process_running and self.readyToStart):
            global global_status;  
            global_status = "Gripper Close";
            self.dobotPlating.gripper.gripperClose();

    def stopProcess(self):
        self.root.quit();

    def popup(self):
        global process_running
        if(not process_running and self.readyToStart):
            self.processThread = thread.start_new_thread(self.dobotPlating.startProcess, (self.ecVoltage, self.pdVoltage, self.rhVoltage,));
    
    def __del__(self):
        if self.processThread is not None:
            self.processThread.exit();
        del self.dobotPlating;

gui = PlatingGUI();
gui.root.mainloop();

