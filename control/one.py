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
    str = ''
    for i in range (len(a)):
        str += chr(a[i])
    arduino.write(str+'#')
    arduino.flushOutput()

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(24) # buffer size is 1024 bytes
    c = struct.unpack("2f",data)

    do_continue = False
    for vel in c:
        if vel > 1:
            do_continue = True
    if do_continue:
        continue
    
    m = np.matrix ([
        [0.5,0.5],
        [0.5,-0.5]])    

    velocidades = m*np.matrix([[c[0]],[c[1]]])
 
    velocidades[0] = -velocidades[0]
    print velocidades
    v = map(lambda x: (x + 1)*90, velocidades)
    print v
    potencias(v)
