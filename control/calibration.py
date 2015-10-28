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
import pygame
from pygame.locals import *
import json


CALIBRATION_FILE = "calibration.json"
calibrating_robot = 0

if os.path.exists(CALIBRATION_FILE):
    with open(CALIBRATION_FILE) as f:
        calibration_obj = json.load(f)
else:
    calibration_obj = [
        {
            "porc_rango_perdido": [0.3, 0.3],   # left and right wheels
            "factores_compensacion": [
                1.0,      # power: 0.0
                1.0,    # power: 0.1
                1.0,    # power: 0.2
                1.0,    # power: 0.3
                1.0,    # power: 0.4
                1.0,    # power: 0.5
                1.0,    # power: 0.6
                1.0,    # power: 0.7
                1.0,    # power: 0.8
                1.0,    # power: 0.9
                1.0,    # power: 0.10
            ]

        },{
            "porc_rango_perdido": [0.3, 0.3],   # left and right wheels
            "factores_compensacion": [
                1.0,      # power: 0.0
                1.0,    # power: 0.1
                1.0,    # power: 0.2
                1.0,    # power: 0.3
                1.0,    # power: 0.4
                1.0,    # power: 0.5
                1.0,    # power: 0.6
                1.0,    # power: 0.7
                1.0,    # power: 0.8
                1.0,    # power: 0.9
                1.0,    # power: 0.10
            ]

        },{
            "porc_rango_perdido": [0.3, 0.3],   # left and right wheels
            "factores_compensacion": [
                1.0,      # power: 0.0
                1.0,    # power: 0.1
                1.0,    # power: 0.2
                1.0,    # power: 0.3
                1.0,    # power: 0.4
                1.0,    # power: 0.5
                1.0,    # power: 0.6
                1.0,    # power: 0.7
                1.0,    # power: 0.8
                1.0,    # power: 0.9
                1.0,    # power: 0.10
            ]

        }
    ]
    with open(CALIBRATION_FILE, 'w+') as f:
        json.dump(calibration_obj, f, indent=4)

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
        # print (a[i])
        str += chr(a[i])
    arduino.write(str+'#')


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


screen = pygame.display.set_mode([200,100])
pygame.display.set_caption("Vsss strategy")
pygame.init()

power = 1.0
team_size = 3
latency = 0.150

def events_loop():
    global power
    global CALIBRATION_FILE, calibrating_robot
    done = False
    send_now = False
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True
        elif e.type == pygame.KEYUP:
            if e.key == pygame.K_ESCAPE:
                done = True
            elif e.key >= pygame.K_0 and e.key <= pygame.K_9:
                power = (e.key - pygame.K_0)/10.0
                if power == 0:
                    power = 1.0
            elif e.key == pygame.K_PLUS or e.key == pygame.K_KP_PLUS:
                power += 0.01
            elif e.key == pygame.K_MINUS or e.key == pygame.K_KP_MINUS:
                power -= 0.01
            elif e.key == pygame.K_m:
                with open(CALIBRATION_FILE, 'w') as f:
                    json.dump(calibration_obj, f, indent=4)
            elif e.key == pygame.K_z:
                calibration_obj[calibrating_robot]["porc_rango_perdido"][0] += 0.01
            elif e.key == pygame.K_x:
                calibration_obj[calibrating_robot]["porc_rango_perdido"][0] -= 0.01
            elif e.key == pygame.K_c:
                calibration_obj[calibrating_robot]["porc_rango_perdido"][1] += 0.01
            elif e.key == pygame.K_v:
                calibration_obj[calibrating_robot]["porc_rango_perdido"][1] -= 0.01
            elif e.key == pygame.K_b:
                calibration_obj[calibrating_robot]["factores_compensacion"][int(power*10)] += 0.01
            elif e.key == pygame.K_n:
                calibration_obj[calibrating_robot]["factores_compensacion"][int(power*10)] -= 0.01
            elif e.key == pygame.K_g:
                calibration_obj[calibrating_robot]["factores_compensacion"][int(power*10)] += 0.1
            elif e.key == pygame.K_h:
                calibration_obj[calibrating_robot]["factores_compensacion"][int(power*10)] -= 0.1
            elif e.key == pygame.K_e:
                calibrating_robot = 0
            elif e.key == pygame.K_r:
                calibrating_robot = 1
            elif e.key == pygame.K_t:
                calibrating_robot = 2
            else:
                send_now = True
    return send_now, done


if __name__ == "__main__":
    prev_send = time.time()
    done = False
    while not done:
        send_now = False
        send_now, done = events_loop()

        if time.time() - prev_send > latency or send_now:
            prev_send = time.time()
            controls = [
                [K_UP, K_DOWN, K_RIGHT, K_LEFT],
                [K_w, K_s, K_d, K_a],
                [K_i, K_k, K_l, K_j]
            ]

            linvel = [0]*team_size
            angvel = [0]*team_size
            for i in range(team_size):
                if pygame.key.get_pressed()[controls[i][0]]:
                    linvel[i] = power
                if pygame.key.get_pressed()[controls[i][1]]:
                    linvel[i] = -power
                if pygame.key.get_pressed()[controls[i][2]]:
                    angvel[i] = power
                if pygame.key.get_pressed()[controls[i][3]]:
                    angvel[i] = -power
            c = []
            for l, a in zip(linvel, angvel):
                c.append(l)
                c.append(a)

            if check(c):
                v = velocidad_to_potencias(c)
                print "\n\n\n\n\n\n"
                print "power", power
                print "calibrating robot", calibrating_robot
                for i, co in enumerate(calibration_obj):
                    print i, co
                vels = []
                for i in range(len(v)):
                    vels.append(struct.unpack('B', chr(v[i]))[0])
                print "output", vels
                potencias(v)
