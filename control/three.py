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

def velocidad_to_potencias (c):
    m = np.matrix ([
        [0.5,0.5],
        [0.5,-0.5]])
    velocidades1 = m*np.matrix([[c[0]],[c[1]]])
    velocidades1[0] = -velocidades1[0]
    velocidades2 = m*np.matrix([[c[2]],[c[3]]])
    velocidades2[0] = -velocidades2[0]
    velocidades3 = m*np.matrix([[c[4]],[c[5]]])
    velocidades3[0] = -velocidades3[0]

    f1 = 1.55
    f2 = 1.55
    f3 = 1.0

    velocidades1[1] *= f1
    n1 = 127.0/max(1, f1)
    v1 = velocidades1*n1 + 128

    v2 = [128, 128]
    v3 = [128, 128]

    return [v1[0],v1[1],v2[0],v2[1],v3[0],v3[1]]

def check (a):
    for i in range (len(a)):
        if abs(a[i])>1.0:
            return False
    return True

while True:
    data, addr = sock.recvfrom(24) # buffer size is 1024 bytes
    c = struct.unpack("6f",data)
    if check(c):
        v = velocidad_to_potencias (c)
        print v
        potencias(v)