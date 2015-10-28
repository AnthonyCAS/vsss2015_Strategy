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


UDP_IP = "0.0.0.0"
UDP_PORT = 9003

CALIBRATION_FILE = "calibration.json"

if os.path.exists(CALIBRATION_FILE):
    with open(CALIBRATION_FILE) as f:
        calibration_obj = json.load(f)
else:
    sys.exit("No hay archivo de calibracion")

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
    global calibration_obj
    m = np.matrix ([
        [0.5,0.5],
        [0.5,-0.5]])
    velocidades = []
    for i in range(3):
        v = m*np.matrix([[c[2*i]],[c[2*i+1]]])
        v[0] = -v[0]
        velocidades.append(v)
    # Tantear. Que porcentaje del rango de potencias es inutil porque el robot no se mueve
    porc_rango_perdidos = [0.4, 0.3, 0.3]


    for i, vel in enumerate(velocidades):
        fsi = calibration_obj[i]["factores_compensacion"][int(10*c[2*i])]
        vel[1] *= fsi

        for j in range(len(vel)):
            rango_perdido = 127.0*calibration_obj[i]["porc_rango_perdido"][j]
            rango_util = 127.0-rango_perdido
            n1 = rango_util/max(1.0, fsi)
            vel[j] = vel[j]*n1
            if vel[j] < 0:
                vel[j] -= rango_perdido
            elif vel[j] > 0:
                vel[j] += rango_perdido
        velocidades[i] = vel + 127
        # print "velocidades ", velocidades

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
        vels = []
        for i in range(len(v)):
            vels.append(struct.unpack('B', chr(v[i]))[0])
        print "output", vels
        potencias(v)