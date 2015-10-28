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



arduino = serial.Serial('/dev/ttyUSB0', baudrate=2400, timeout=1.0)
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
    velocidades = []
    for i in range(3):
        v = m*np.matrix([[c[2*i]],[c[2*i+1]]])
        v[0] = -v[0]
        velocidades.append(v)

    # Tantear. Factor para igualar la potencia de ambas llantas
    fs = [7.0, 1.55, 1.0]
    # Tantear. Que porcentaje del rango de potencias es inutil porque el robot no se mueve
    porc_rango_perdidos = [0.4, 0.3, 0.3]


    for i, vel in enumerate(velocidades):
        rango_perdido = 127.0*porc_rango_perdidos[i]
        rango_util = 127.0-rango_perdido
        vel[1] *= fs[i]

        n1 = rango_util/max(1.0, fs[i])
        vel = vel*n1
        for j in range(len(vel)):
            if vel[j] < 0:
                vel[j] -= rango_perdido
            elif vel[j] > 0:
                vel[j] += rango_perdido
        velocidades[i] = vel + 127
        print "velocidades ", velocidades

    return [x for vel in velocidades for x in vel]


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
        print "Sale ", v
        potencias(v)