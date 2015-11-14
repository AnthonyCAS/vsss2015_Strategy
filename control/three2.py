# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 03:26:51 2015

@author: victo
"""

import numpy as np
import socket
import struct
import serial
import time
import os
import json
import sys
from control_simple import velocidad_to_potencias


UDP_IP = "0.0.0.0"
UDP_PORT = 9003

arduino = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1.0)
arduino.setDTR(False)
time.sleep(1)
arduino.flushInput()
arduino.setDTR(True)


def potencias(a):
    global arduino
    arduino.flushOutput()
    str = ''
    for i in range (len(a)):
        print (a[i])
        str += chr(a[i])
    arduino.write(str+'#')

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))



def check (a):
    for i in range (len(a)):
        if abs(a[i])>1.0:
            return False
    return True

while True:
    data, addr = sock.recvfrom(24) # buffer size is 1024 bytes
    c = struct.unpack("6f",data)
    print "Llego ", c
    if check(c):
        v = velocidad_to_potencias (c)
        vels = []
        for i in range(len(v)):
            vels.append(struct.unpack('B', chr(v[i]))[0])
        print "output", vels
        potencias(v)