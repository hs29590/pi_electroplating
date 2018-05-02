#! /usr/bin/env python
from glob import glob
import time
import sys
import serial
import math
#from Tkinter import *
from tkinter import *
from tkinter import ttk
#import ttk
import _thread
from DigitalVoltControl import DigitalVoltControl
from Relay import Relay
from ServoGripper import ServoGripper
from pydobot import Dobot

global_status = "Running";
global_step_indicator = "None";
process_running = False;

R_OFFSET = 20;

PROCESS_RH_PD = 'PD_Rh_Silver';
PROCESS_RH_20 = 'Rh_Redip';
PROCESS_RH_60 = 'Rh_White_Gold';


#x,y,z,r,duration

Beakers = [ [0, 0, 0, 0, 0],      #0 dummy beaker for numbering
            [-16.3, -214.8, 0, -197.2+R_OFFSET - 20, 60], #1 # -135deg
            [39.67, -290.2, 0, -185.15+R_OFFSET -10, 5],  #2 #  -112.6deg
            [119.48, -173.56, 0, -158.4+R_OFFSET- 10, 5], #3 # -90deg
            [185.99, -193, 0, -122+R_OFFSET-10, 10], #4 # -67.6deg
            [187.12, -66.2, 0, -96.4+R_OFFSET-10, 5], #5 # -45deg
            [272.41, -13.6, 0, -79.9+R_OFFSET-10, 5],  #6 # -22.6deg
            [211, -74.7, 0, 30.3+R_OFFSET-5, 5],    #7 # 0deg
            [271.42, 34.54, 0, 32.1+R_OFFSET, 60],  #8 # 22.4deg
            [198.72, 70.09, 0, 65+R_OFFSET, 5],   #9 # 45deg
            [193.53, 206.47, 0, 92.4+R_OFFSET-2, 5],    #10 # 67.4deg
            [-75.58, 242.89, 0, 152.8+R_OFFSET-5, 60], #11 # 130deg
            [75.54, 183.83, 0, 113.22+R_OFFSET+5, 5]]; #12 #97deg


class DobotPlating():
    def __init__(self, dobotPort='/dev/ttyUSB0'):
        available_ports = glob('/dev/tty*USB*')  # mask for OSX Dobot port
        if len(available_ports) == 0:
            print('no port /dev/tty*USB* found for Dobot Magician')
            exit(1)
        else:
            dobotPort = available_ports[0];

        #self.DobotPort = 'COM4'
        self.DobotPort = dobotPort;

        self.ecRelay = Relay(18);#bcm pin for physical pin 12
        self.pdRelay = Relay(24);#bcm for physical 18
        self.rhRelay = Relay(23);#bcm for physical 16
        self.gripper = ServoGripper(2);
        self.dvc = DigitalVoltControl();

        self.RH_Duration = 60;
        self.PD_DURATION = 60;

        self.lastCmd = [0,0,0,0]; #x, y, z, r
    
        print("Setting Port to " + self.DobotPort);
        self.device = Dobot(port=self.DobotPort)
        time.sleep(1)
        if self.device is not None:
            print("Opened connection")

        self.device.speed()

        self.z_up = 100
        self.z_down = -70
        #self.RH_Voltage = 2.5;
        #self.PD_Voltage = 1.9;
        #self.EC_Voltage = 4.8;
        
        self.home_xyzr = [215, 0, self.z_up, 0];                    
        global global_status
        global_status = "Rh Electroplating";
    
    def calibrate(self):
        global global_status
        response = self.device.setHomeParams(self.home_xyzr[0], self.home_xyzr[1], self.home_xyzr[2], self.home_xyzr[3]);
#if(response):
#           global_status = "Error..";

        response = self.device.goHome();
#        if(response):
#            global_status = "Error..";

    def isMoveFinished(self):
        global global_step_indicator;
        global_step_indicator = "isMoveFinished";
        
        euDist = math.pow(self.lastCmd[0] - self.device.x,2) + math.pow(self.lastCmd[1] - self.device.y, 2) + math.pow(self.lastCmd[2] - self.device.z, 2) + math.pow(self.lastCmd[3] - self.device.r, 2);
        euDist = math.sqrt(euDist);
        if(euDist < 10):
            return True;
        else:
            #print("still moving ..");
            return False;
        
    def move_home(self):
        global global_step_indicator;
        global_step_indicator = "move_home";
        self.move_xy(self.home_xyzr[0], self.home_xyzr[1], self.home_xyzr[2], self.home_xyzr[3], 0.3);

    def move_xy(self, x, y, z, r, duration = 1):
        global global_step_indicator;
        global_step_indicator = "move_xy";
        self.lastCmd = [x, y, z, r];
        response = self.device.go(x, y, z, r);  #MOVJ
#        if(response):
#            global global_status
#            global_status = "Error..";

#        time.sleep(duration);
#            print("in is move finished..");
        print("xyzr position: " + str(self.device.x) + ", " + str(self.device.y) + ", " + str(self.device.z) + ", " + str(self.device.r));
   
    def move_xy_linear(self, x, y, z, r, duration = 1):
        self.lastCmd = [x, y, z, r];
        response = self.device.goMovL(x, y, z, r);  #MOVJ
#        if(response):
#            global global_status
#            global_status = "Error..";
#        time.sleep(duration);
#            print("in is move finished..");
        print("xyzr position: " + str(self.device.x) + ", " + str(self.device.y) + ", " + str(self.device.z) + ", " + str(self.device.r));
        
    def shake(self, x, y, z, r, shakeDuration, dispStr, dontShake=False, doInOut=False):
        global global_step_indicator;
        global_step_indicator = "shake ";
        global global_status;
        t_end = time.time() + shakeDuration;
        tdiff = t_end - time.time();
        while tdiff > 0:
            if(dispStr is not None):
                global_status = dispStr + " " + str(int(tdiff)) + "s"
            if(not dontShake):
                self.move_xy(x, y, z + 10, r, 0.1);
                self.move_xy(x, y, z - 10, r, 0.1);
            tdiff = t_end - time.time();
    
    def shakeHalfUp(self, x, y, z, r, shakeDuration, dispStr, dontShake=False, doInOut=False):
        global global_step_indicator;
        global_step_indicator = "shake ";
        global global_status;
        t_end = time.time() + shakeDuration;
        tdiff = t_end - time.time();
        while tdiff > 0:
            if(dispStr is not None):
                global_status = dispStr + " " + str(int(tdiff)) + "s"
            if(not dontShake):
                self.move_xy(x, y, (self.z_up + self.z_down)/2.0, r, 0.1);
                self.move_xy(x, y, z - 10, r, 0.1);
            tdiff = t_end - time.time();
        
    def up_down_beaker(self,id,dispStr=None):

        print ("Doing beaker %d now" % (id));
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_up, Beakers[id][3], 0.3);
        self.move_xy(Beakers[id][0], Beakers[id][1], (self.z_up + self.z_down)/2.0 , Beakers[id][3], 0.3); #adding a mid point so that the Joint motion isn't touching th edges of the beakers
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_down, Beakers[id][3], 0.3);
        #dispStr = "Step " + str(id) + ": ";

        t_end = time.time() + 25;
        while(not self.isMoveFinished()):
            time.sleep(0.01);
            if(time.time() > t_end):
                global global_step_indicator;
                global_step_indicator = "timing error..";
                break;

        global global_step_indicator;
        global_step_indicator = "up_down_beaker " + str(id);

        if(id == 1):
            self.ecRelay.on();
        #    dispStr = dispStr + "EC "
        elif(id == 8):
            self.pdRelay.on();
        #    dispStr = dispStr + "Pd Solution "
        elif(id == 11):
            self.rhRelay.on();
        #    dispStr = dispStr + "Rh Solution "
            
        if(id == 1 or id == 8 or id == 11):
            if(id == 11):
                self.shake(Beakers[id][0], Beakers[id][1], self.z_down - 10, Beakers[id][3], self.RH_Duration, dispStr); #x, y, z and shake_duration
            elif(id == 1): #dont' shake
                self.shake(Beakers[id][0], Beakers[id][1], self.z_down, Beakers[id][3], Beakers[id][4], dispStr, True); #x, y, z and shake_duration
            else: #this means id is 8 i.e. Pd
                self.shake(Beakers[id][0], Beakers[id][1], self.z_down, Beakers[id][3], self.PD_Duration, dispStr); #x, y, z and shake_duration
        else:    
            self.shakeHalfUp(Beakers[id][0], Beakers[id][1], self.z_down, Beakers[id][3], Beakers[id][4], None); #x, y, z and shake_duration
        
        global global_step_indicator;
        global_step_indicator = "bottom_shake_finished";
        
        self.ecRelay.off();
        self.pdRelay.off();
        self.rhRelay.off();
        #move up
        
        #shake to drop the excess drops
        #go half way to adjust for MOVJ
        self.move_xy(Beakers[id][0], Beakers[id][1], (self.z_up + self.z_down)/2.0 , Beakers[id][3], 0.3); #adding a mid point so that the Joint motion isn't touching th edges of the beakers
        #self.move_xy(Beakers[id][0], Beakers[id][1], self.z_up, Beakers[id][3]);

        self.shake(Beakers[id][0], Beakers[id][1], self.z_up, Beakers[id][3], 2, None);
        
        self.move_xy(Beakers[id][0], Beakers[id][1], self.z_up, Beakers[id][3]);
        
        global_step_indicator = "excess_shake_finished";
        
        t_end = time.time() + 25;
        while(not self.isMoveFinished()):
            time.sleep(0.01);
            if(time.time() > t_end):
                global global_step_indicator;
                global_step_indicator = "timing error..";
                break;
        
        global_step_indicator = "excess_shake_move_finished";
     
    def startProcess(self, EC_Voltage, PD_Voltage, RH_Voltage, processType, pdTimeToDo, rhTimeToDo):
        global process_running
        process_running = True;
        global global_status

        self.RH_Duration = rhTimeToDo;
        #if(processType == PROCESS_RH_20):
        #    self.RH_Duration = 20;
        self.PD_Duration = pdTimeToDo;
        

        global_status = "Step 1: EC"
        #1
        if(EC_Voltage == 5.6):
            self.dvc.setMaxVoltage();
        else:
            self.dvc.setVoltage(EC_Voltage);
        self.up_down_beaker(1, global_status);
        
        #2
        global_status = "Step 2: Dragout"
        self.up_down_beaker(2);
        
        #3
        global_status = "Step 3: Water"
        self.up_down_beaker(3);

        #4
        global_status = "Step 4: Activation"
        self.up_down_beaker(4);
        
        #5
        global_status = "Step 5: Water"
        self.up_down_beaker(5);

        #6
        global_status = "Step 6: Water"
        self.up_down_beaker(6);
        
        #7
        global_status = "Step 7: Water"
        self.up_down_beaker(7);

        #8
        if(processType == PROCESS_RH_PD):
            global_status = "Step 8: Pd Solution"
            self.dvc.setVoltage(PD_Voltage);
            self.up_down_beaker(8, global_status);
        
            #9
            global_status = "Step 9: Pd Dragout"
            self.up_down_beaker(9);
        
            #10
            global_status = "Step 10: Water"
            self.up_down_beaker(10);
        
        #11
        if(processType == PROCESS_RH_PD):
            global_status = "Step 11: Rh Solution"
        else:
            global_status = "Step 8: Rh Solution"
        self.dvc.setVoltage(RH_Voltage);
        self.up_down_beaker(11, global_status);
        
        #12
        if(processType == PROCESS_RH_PD):
            global_status = "Step 12: Rh Dragout"
        else:
            global_status = "Step 9: Rh Dragout"
        self.up_down_beaker(12);
        
        #13 #repeat of beaker 10
        if(processType == PROCESS_RH_PD):
            global_status = "Step 13: Water"
        else:
            global_status = "Step 10: Water"
        self.up_down_beaker(10);

        #Home
        self.move_home()
        global_status = "Done.."
        process_running = False;
        print("\n DONE \n");
   
    def __del__(self):
        self.device.close();        
        del self.gripper;
        del self.dvc;
        del self.ecRelay;
        del self.pdRelay;
        del self.rhRelay;
        print("Exiting Cleanly..");
           

class PlatingGUI():
    def __init__(self):
        self.root = Tk()
        self.root.title("Rh Electroplating")
        
        self.calibrated = True;

        framew = 500; # root w
        frameh = 400; # root h
        screenw = self.root.winfo_screenwidth();
        screenh = self.root.winfo_screenheight();
        posx = (screenw/2) - (framew/2);
        posy = (screenh/2) - (frameh/2);
        self.root.geometry( "%dx%d+%d+%d" % (framew,frameh,posx,posy))

        self.current_status = StringVar();
        self.current_status.set('Rh Electroplating');

        self.stepIndicator = StringVar();
        self.stepIndicator.set('_init_');

        self.mainframe = ttk.Frame(self.root, padding="10 10 30 30", height=400, width=500)
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=50,minsize=50)
        self.mainframe.rowconfigure(0, weight=50,minsize=50)
        #self.mainframe.grid_propagate(0);

        self.buttonStyle = ttk.Style()
        self.buttonStyle.configure('my.TButton', font=('Helvetica', 18))
        
        self.l = ttk.Label(self.mainframe, textvariable=self.current_status, font=('Helvetica',18));
        #self.l.place(relx=0.35, rely=0.3, anchor='center')
        self.l.grid(row=0, column=0, columnspan=2, pady=5)

        self.ecvar = StringVar(self.root)
        self.pdvar = StringVar(self.root)
        self.rhvar = StringVar(self.root)
        self.processType = StringVar(self.root)
       
        self.pdTime = StringVar(self.root)
        self.rhTime = StringVar(self.root)

        ecchoices = {'5.6'}
        pdchoices = { '1.8','1.9','2.0','2.1'}
        rhchoices = { '2.2', '2.3', '2.4','2.5','2.6','2.75','2.85','3.0'}
        processChoices = {PROCESS_RH_PD, PROCESS_RH_60, PROCESS_RH_20};
        pdTimeChoices = {'30','40','50','60'}
        rhTimeChoices = {'20','30','40','50','60'}
       
        self.ecvar.set('5.6') # set the default option
        self.pdvar.set('1.9')
        self.rhvar.set('2.5')
        self.processType.set(PROCESS_RH_PD);
        self.pdTime.set('60');
        self.rhTime.set('60');
        
        self.ecVoltage = float(self.ecvar.get());
        self.pdVoltage = float(self.pdvar.get());
        self.rhVoltage = float(self.rhvar.get());
        self.pdTimeToDo = int(self.pdTime.get());
        self.rhTimeToDo = int(self.rhTime.get());
        self.processToDo = self.processType.get();
        
        processChoicepopupMenu = OptionMenu(self.mainframe, self.processType, *processChoices)
        Label(self.mainframe, text="Choose Process", font=("Helvetica", 14)).grid(row = 2, column=1, pady=(15,2))
        processChoicepopupMenu.grid(row=3, column=1)
        processChoicepopupMenu.bind('<Button-1>', self.dropdownopen)
        
        pdpopupMenu = OptionMenu(self.mainframe, self.pdvar, *pdchoices)
        Label(self.mainframe, text="Pd Voltage", font=("Helvetica", 14)).grid(row = 5, column = 0, pady=(15,2))
        pdpopupMenu.grid(row = 6, column =0)
        pdpopupMenu.bind('<Button-1>', self.dropdownopen)
        
        rhpopupMenu = OptionMenu(self.mainframe, self.rhvar, *rhchoices)
        Label(self.mainframe, text="Rh Voltage", font=("Helvetica", 14)).grid(row = 5, column = 1, pady=(15,2))
        rhpopupMenu.grid(row = 6, column=1)
        rhpopupMenu.bind('<Button-1>', self.dropdownopen)
        
        rhTimeMenu = OptionMenu(self.mainframe, self.rhTime, *rhTimeChoices)
        Label(self.mainframe, text="Rh Time (s)", font=("Helvetica", 14)).grid(row = 8, column = 1, pady=(15,2))
        rhTimeMenu.grid(row = 9, column=1)
        rhTimeMenu.bind('<Button-1>', self.dropdownopen)
        
        pdTimeMenu = OptionMenu(self.mainframe, self.pdTime, *pdTimeChoices)
        Label(self.mainframe, text="Pd Time (s)", font=("Helvetica", 14)).grid(row = 8, column = 0, pady=(15,2))
        pdTimeMenu.grid(row = 9, column=0)
        pdTimeMenu.bind('<Button-1>', self.dropdownopen)
        
        self.ecvar.trace('w', self.ec_change)
        self.pdvar.trace('w', self.pd_change)
        self.rhvar.trace('w', self.rh_change)
        self.pdTime.trace('w', self.pd_time_change)
        self.rhTime.trace('w',self.rh_time_change)
        self.processType.trace('w', self.process_change)

        ttk.Button(self.mainframe, text="Calibrate", style='my.TButton', command=self.calibrateDobot, width=16).grid(row=2, rowspan=2, column=0, pady=5)
        ttk.Button(self.mainframe, text="Start", style='my.TButton',command=self.popup, width=16).grid(row=10, rowspan=2,column=0, pady=(20,2))
        ttk.Button(self.mainframe, text="Exit", style='my.TButton', command=self.stopProcess, width=16).grid(row=10, rowspan=2, column=1, pady=(20,2))
        
        self.processStepIndicator = ttk.Label(self.mainframe, textvariable=self.stepIndicator, font=('Helvetica',7));
        self.processStepIndicator.grid(row=13,column=1,pady=5)
  
        self.root.after(1000, self.updateLabel);
    
        self.dobotPlating = DobotPlating();
    
    def calibrateDobot(self):
        global process_running
        if(not process_running):
            print('Will Calibrate now..');
            global global_status;  
            global_status = "Calibrating.. Please Wait!";
            self.dobotPlating.calibrate();
            time.sleep(20);
            self.calibrated = True;
            global_status = "Calibrated";

    def dropdownopen(self, event):
        global process_running
        if(process_running):
            self.toplevel = Toplevel()
            self.toplevel.wm_attributes("-topmost", 1) 
            framew = 300; # root w
            frameh = 75; # root h
            screenw = self.root.winfo_screenwidth();
            screenh = self.root.winfo_screenheight();
            posx = (screenw/2) - (framew/2);
            posy = (screenh/2) - (frameh/2);
            self.toplevel.geometry( "%dx%d+%d+%d" % (framew,frameh,posx,posy))
            self.label1 = Label(self.toplevel, text="Can't change value when process is running..", height=0, width=100)
            self.label1.pack(padx=5)
            self.but1 = Button(self.toplevel, text="OK", command=self.dropdownokpressed);
            self.but1.pack(pady=5);


    def initialPopup(self):
        self.toplevel = Toplevel()
        self.toplevel.wm_attributes("-topmost", 1) 
        framew = 300; # root w
        frameh = 75; # root h
        screenw = self.root.winfo_screenwidth();
        screenh = self.root.winfo_screenheight();
        posx = (screenw/2) - (framew/2);
        posy = (screenh/2) - (frameh/2);
        self.toplevel.geometry( "%dx%d+%d+%d" % (framew,frameh,posx,posy))
        #self.toplevel.geometry("300x75+500+500");
        self.label1 = Label(self.toplevel, text="Please Calibrate First!", font=("Helvetica",14), height=0, width=100)
        self.label1.pack(padx=5)
        self.but1 = Button(self.toplevel, text="OK", command=self.dropdownokpressed);
        self.but1.pack(pady=5);
        
    def dropdownokpressed(self):
        self.toplevel.destroy();

    def ec_change(self,*args):
        self.ecVoltage = float(self.ecvar.get());
        print( 'EC Volt set to '),
        print (self.ecVoltage)

    def rh_time_change(self, *args):
        self.rhTimeToDo = int(self.rhTime.get());
        print('Rh Time changed to: ');
        print (self.rhTimeToDo);
    
    def pd_time_change(self, *args):
        self.pdTimeToDo = int(self.pdTime.get());
        print('Pd Time changed to: ');
        print (self.pdTimeToDo);

    def process_change(self, *args):
        self.processToDo = self.processType.get();
        print ('Process changed to: '),
        print (self.processToDo);

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
        self.l.grid(row=0)
        self.l.update_idletasks();
    
        global global_step_indicator;
        self.stepIndicator.set(global_step_indicator);
        self.processStepIndicator.config(textvariable=self.stepIndicator);
        self.processStepIndicator.update_idletasks();

        self.root.update_idletasks();
        self.root.after(500, self.updateLabel);

    def stopProcess(self):
        del self.dobotPlating
        self.root.quit();
        exit(1);

    def popup(self):
        global process_running
        if(not process_running and self.calibrated):
           self.processThread = _thread.start_new_thread(self.dobotPlating.startProcess, (self.ecVoltage, self.pdVoltage, self.rhVoltage, self.processToDo, self.pdTimeToDo, self.rhTimeToDo));
        else:
            self.initialPopup();
    
    def __del__(self):
        if self.processThread is not None:
            self.processThread.exit();
        del self.dobotPlating;
        print("GUI Exited Cleanly..");

gui = PlatingGUI();
gui.root.mainloop();

