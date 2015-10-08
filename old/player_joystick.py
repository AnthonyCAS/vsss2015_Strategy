#!/usr/bin/python

import pygame
import socket
import struct
import time
import sys
from pygame.locals import *

from vsss.serializer import VsssSerializer, VsssOutData
from vsss.core import Move, RED_TEAM, BLUE_TEAM


VISION_SERVER = ('', 9009)
CONTROL_SERVER = ('', 9009)
THIS_SERVER = ('', 9091)

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)


pygame.init()
screen = pygame.display.set_mode((100, 100))

prev_time = time.time() * 1000 # milliseconds

LIN_VEL = 50
ANG_VEL = 3

red_serializer = VsssSerializer(team_size=3, my_team=RED_TEAM)
blue_serializer = VsssSerializer(team_size=3, my_team=BLUE_TEAM)

# allow multiple joysticks
joy = []

pygame.joystick.init()
print pygame.joystick.get_count()
if not pygame.joystick.get_count():
    print "\nPlease connect ONE joystick and run again.\n"
    quit()
print "\n%d joystick(s) detected." % pygame.joystick.get_count()
for i in range(pygame.joystick.get_count()):
    myjoy = pygame.joystick.Joystick(i)
    myjoy.init()
    joy.append(myjoy)
    print "Joystick %d: " % (i) + joy[i].get_name()
print "Depress trigger (button 0) to quit.\n"


done = False
axis = [{'x': 0, 'y': 0},
        {'x': 0, 'y': 0}]

while not done:
    for event in pygame.event.get():
        # any other key event input
        if event.type == QUIT:
            done = True
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                done = True
        elif (event.type == pygame.JOYAXISMOTION or
              event.type == pygame.JOYBUTTONDOWN):
            i = event.dict['joy']
            if event.dict.has_key('axis') and event.dict.has_key('value'):
                if (event.dict['axis'] == 1):
                    axis[i]['x'] = event.dict['value']
                elif (event.dict['axis'] == 0):
                    axis[i]['y'] = event.dict['value']

    red_move = Move()
    red_move.linvel = -LIN_VEL*axis[0]['x']
    red_move.angvel = -ANG_VEL*axis[0]['y']

    blue_move = Move()
    blue_move.linvel = -LIN_VEL*axis[1]['x']
    blue_move.angvel = -ANG_VEL*axis[1]['y']

    out_red = VsssOutData()
    out_red.moves.append(Move())
    out_red.moves.append(Move())
    out_red.moves.append(red_move)

    out_blue = VsssOutData()
    out_blue.moves.append(Move())
    out_blue.moves.append(Move())
    out_blue.moves.append(blue_move)

    out_red = red_serializer.dump(out_red)
    out_blue = blue_serializer.dump(out_blue)

    cur_time = time.time() * 1000 # milliseconds
    if cur_time - prev_time > 100:
        prev_time = cur_time
        sock.sendto(out_red, CONTROL_SERVER)
        sock.sendto(out_blue, CONTROL_SERVER)
