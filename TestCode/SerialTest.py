#!/usr/bin/env python3
import serial

## Need: Debugging to catch a changing serial path

if __name__ == '__main__':s
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)