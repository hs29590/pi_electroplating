import sys
import time
import threading

class ReadFromScanner():

    def __init__(self, port):
        self.hid = { 4: 'S', 5: 'B', 6: 'C', 7: 'D', 8: 'E', 9: 'F', 10: 'G', 11: 'H', 12: 'I', 13: 'J', 14: 'K', 15: 'L', 16: 'M', 17: 'N', 18: 'O', 19: 'P', 20: 'Q', 21: 'R', 22: 'S', 23: 'T', 24: 'U', 25: 'V', 26: 'W', 27: 'X', 28: 'Y', 29: 'Z', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9', 39: '0', 44: ' ', 45: '-', 46: '=', 47: '[', 48: ']', 49: '\\', 51: ';' , 52: '\'', 53: '~', 54: ',', 55: '.', 56: '/'  }
        self.fp = open(port, 'rb')
        self.decodedString = '';
        t1 = threading.Thread(target=self.readThread);
        t1.daemon = True;
        t1.start()
    
    def __del__(self):
        self.fp.close();

    def readThread(self):
        while True:
            buffer = self.fp.read(8)
            for c in buffer:
                if ord(c) > 0:
                    try:
                        self.decodedString = self.decodedString + self.hid[int(ord(c))]
                    except:
                        #print "passing ", str(ord(c))
                        pass

    def startRead(self):
        self.decodedString = '';

    def finishRead(self):
        print(self.decodedString);

R = ReadFromScanner('/dev/hidraw0')
while(True):
    a = raw_input('Press Enter to Start Read');
    R.startRead();
    b = raw_input('Press Enter when Read Finished or Q to exit');
    R.finishRead();
    if(b == 'q' or b == 'Q'):
        break;
    

