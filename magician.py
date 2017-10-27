import time
from glob import glob

from pydobot import Dobot

available_ports = glob('/dev/tty*USB*')  # mask for OSX Dobot port
if len(available_ports) == 0:
    print('no port found for Dobot Magician')
    exit(1)

z_up = 20
z_down = 0

home_xyzr = [215, 0, 100, 0];

#x,y,z,r

Beakers = [ [0, 0, 0, 0],      #0 dummy beaker for numbering
            [-16.3, -214.8, 0, -197.2], #1 # -135deg
            [39.67, -290.2, 0, -185.15],  #2 #  -112.6deg
            [119.48, -173.56, 0, -158.4], #3 # -90deg
            [185.99, -193, 0, -122], #4 # -67.6deg
            [187.12, -66.2, 0, -96.4], #5 # -45deg
            [272.41, -13.6, 0, -79.9],  #6 # -22.6deg
            [211, -74.7, 0, 30.3],    #7 # 0deg
            [271.42, 34.54, 0, 32.1],  #8 # 22.4deg
            [198.72, 70.09, 0, 65],   #9 # 45deg
            [193.53, 206.47, 0, 92.4],    #10 # 67.4deg
            [-75.58, 242.89, 0, 152.8], #11 # 130deg
            [75.54, 183.83, 0, 113.22]]; #12 #97deg


device = Dobot(port=available_ports[0])
time.sleep(1)

device.go(home_xyzr[0], home_xyzr[1], home_xyzr[2], home_xyzr[3]);

    
def up_down_beaker(id):
    print ("Doing beaker " + str(id) + " now");
    device.go(Beakers[id][0], Beakers[id][1], z_up, Beakers[id][3]);
    device.go(Beakers[id][0], Beakers[id][1], z_down, Beakers[id][3]);

time.sleep(1)
device.speed(30)

#up_down_beaker(1);
up_down_beaker(2);
up_down_beaker(3);
up_down_beaker(4);
up_down_beaker(5);
up_down_beaker(6);
up_down_beaker(7);
#set pd voltage
up_down_beaker(8);
up_down_beaker(9);
up_down_beaker(10);
#set Rh voltage
#up_down_beaker(11);
up_down_beaker(12);
device.go(home_xyzr[0], home_xyzr[1], home_xyzr[2], home_xyzr[3]);

device.close()
