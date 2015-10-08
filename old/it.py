#!/usr/bin/env python
#
# joystick-servo.py
#
# created 19 December 2007
# copyleft 2007 Brian D. Wendt
# http://principialabs.com/
#
# code adapted from:
# http://svn.lee.org/swarm/trunk/mothernode/python/multijoy.py
#
# NOTE: This script requires the following Python modules:
#  pyserial - http://pyserial.sourceforge.net/
#  pygame   - http://www.pygame.org/
# Win32 users may also need:
#  pywin32  - http://sourceforge.net/projects/pywin32/
#

import serial
import pygame

# allow multiple joysticks
joy = []

# Arduino USB port address (try "COM5" on Win32)
usbport = "COM17"

# define usb serial connection to Arduino
ser = serial.Serial(usbport, 9600)

# handle joystick event
def handleJoyEvent(e):
    if e.type == pygame.JOYAXISMOTION:
        axis = "unknown"
        if (e.dict['axis'] == 1):
            axis = "X"

        if (e.dict['axis'] == 0):
            axis = "Y"

        if (e.dict['axis'] == 2):
            axis = "Throttle"

        if (e.dict['axis'] == 3):
            axis = "Z"

        if (axis != "unknown"):
            str = "Axis: %s; Value: %f" % (axis, e.dict['value'])
            # uncomment to debug
            output(str, e.dict['joy'])

            # Arduino joystick-servo hack
            if (axis == "X"):
                posX = e.dict['value']
                # convert joystick position to servo increment, 0-254
                moveX = round(posX * 127, 0)
                if (moveX < 0):
                    servoX = int(127 - abs(moveX))
                else:
                    servoX = int(moveX + 127)
                # convert position to ASCII character
                servoPositionX = chr(servoX)
                # and send to Arduino over serial connection
                ser.write(chr(1)+servoPositionX)
                
                # uncomment to debug
                #print servoX, servoPositionX
            if (axis == "Z"):
                posZ = e.dict['value']
                # convert joystick position to servo increment, 0-254
                moveZ = round(posZ * 127, 0)
                if (moveZ < 0):
                    servoZ = int(127 - abs(moveZ))
                else:
                    servoZ = int(moveZ + 127)
                # convert position to ASCII character
                servoPositionZ = chr(servoZ)
                # and send to Arduino over serial connection
                ser.write(chr(2)+servoPositionZ)
            #cad = servoPositionX + servoPositionZ
            #ser.write(cad)
                
                # uncomment to debug
                #print servoZ, servoPositionZ

    elif e.type == pygame.JOYBUTTONDOWN:
        str = "Button: %d" % (e.dict['button'])
        # uncomment to debug
        output(str, e.dict['joy'])
        # Button 0 (trigger) to quit
        if (e.dict['button'] == 0):
            print "Bye!\n"
            ser.close()
            quit()
    else:
        pass

# print the joystick position
def output(line, stick):
    print "Joystick: %d; %s" % (stick, line)

# wait for joystick input
def joystickControl():
    while True:
        e = pygame.event.wait()
        if (e.type == pygame.JOYAXISMOTION or e.type == pygame.JOYBUTTONDOWN):
            handleJoyEvent(e)

# main method
def main():
    # initialize pygame
    pygame.joystick.init()
    pygame.display.init()
    if not pygame.joystick.get_count():
        print "\nPlease connect a joystick and run again.\n"
        quit()
    print "\n%d joystick(s) detected." % pygame.joystick.get_count()
    for i in range(pygame.joystick.get_count()):
        myjoy = pygame.joystick.Joystick(i)
        myjoy.init()
        joy.append(myjoy)
        print "Joystick %d: " % (i) + joy[i].get_name()
    print "Depress trigger (button 0) to quit.\n"

    # run joystick listener loop
    joystickControl()

# allow use as a module or standalone script
if __name__ == "__main__":
    main()
