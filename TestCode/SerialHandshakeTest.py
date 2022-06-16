#!/usr/bin/env python3
import serial
import time
import json
## Need: Debugging to catch a changing serial path

if __name__ == '__main__':
    try:
        ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    except serial.SerialException:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        ser.write(b"GO\n")
        line = ser.readline().decode('utf-8').rstrip()
        
        if line == "GO" :
            data = ser.readline().decode('utf-8').rstrip()
            datadict = json.loads(data)
            print(datadict,type(datadict))
        time.sleep(2)