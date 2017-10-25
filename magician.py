import time
from glob import glob

from pydobot import Dobot

available_ports = glob('/dev/tty*USB*')  # mask for OSX Dobot port
if len(available_ports) == 0:
    print('no port found for Dobot Magician')
    exit(1)

z_up = 20
z_down = 0

home_xyz = [215, 0, 100];

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


device = Dobot(port=available_ports[0])
time.sleep(1)

device.go(home_xyz[0], home_xyz[1], home_xyz[2]);

    
def up_down_beaker(id):
    print ("Doing beaker " + str(id) + " now");
    device.go(Beakers[id][0], Beakers[id][1], z_up);
    device.go(Beakers[id][0], Beakers[id][1], z_down);

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
device.go(home_xyz[0], home_xyz[1], home_xyz[2]);

device.close()
