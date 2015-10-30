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
from control_simple import velocidad_to_potencias


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
        # print (a[i])
        str += chr(a[i])
    arduino.write(str+'#')


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
latency = 0.200

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
                vels = []
                for i in range(len(v)):
                    vels.append(struct.unpack('B', chr(v[i]))[0])
                print "output", vels
                potencias(v)
