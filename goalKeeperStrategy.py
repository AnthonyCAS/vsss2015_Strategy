#!/usr/bin/python

import socket
import sys
import time

import threading

from vsss.controller import Controller
from vsss.position import RobotPosition, Position

from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData, VsssInData
from stateMachine import *

RED_TEAM = 0
BLUE_TEAM = 1

class stateMachine:
    def __init__(self):
        self.state = None

    def do_move(self, player, ball, objetive, controller):
        return self.state(player, ball, objetive, controller)

DefensorState = stateMachine()
#forwardState = stateMachine()

def shootingBall(currentPosition, ballPosition, objetive, controller):
    if currentPosition.distance_to(ballPosition) < 5:
        return controller.go_to_from(ballPosition, currentPosition)

def go_to_ball(currentPosition, ballPosition, objetive, controller):
    return controller.go_to_from(ballPosition, currentPosition)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

'''
Methods to manage the robot moves
'''
def get_defensor_move(color, currentPosition, ballPosition, objetive, controller):
    if abs(currentPosition.x - ballPosition.x) > 75:
        if abs(currentPosition.y - ballPosition.y) > 65:
            DefensorState.state = go_to_ball
        elif (abs(currentPosition.angle_to(objetive) - ballPosition.angle_to(objetive)) < 1 and
                      currentPosition.distance_to(objetive) > ballPosition.distance_to(objetive)):
            DefensorState.state = shootingBall
        else:
            DefensorState.state = None # estado
            return Move(0.1, 0.1)
    else:
        return Move(0.1, 0.1)

    move = DefensorState.do_move(currentPosition, ballPosition, objetive, controller)
    return move


def get_goalKeeper_move(color, currentPosition, ballPosition, objetive, controller):
    newPosition = RobotPosition(ballPosition.x, ballPosition.y)
    newPosition.theta = 90

    newPosition.y = min(16.5, max(-16.5, newPosition.y))
    if color == RED_TEAM:
        newPosition.x = 68
        return controller
    else:
        newPosition.x = -68
    return controller.go_to_from(newPosition, currentPosition)


class MoveThread (threading.Thread):
    def __init__(self, typeMove):
        threading.Thread.__init__(self)
        self.move = typeMove
    def run(self):
    	pass
        #self.move()
        

def run():
	pass
'''
thread = MoveThread(typeMove)
thread.start() '''
		
class GKStrategy(TeamStrategyBase):
    use_control = True
    do_visualize = True
    use_vision = True

    THIS_SERVER = ('127.0.0.1', 9002)
    VISION_SERVER = ('127.0.0.1', 9001)
    CONTROL_SERVER = ('127.0.0.1', 9001)


    serializer_class = VsssSerializerSimulator

    def strategy(self, data):
        print data.teams


    def set_up(self):
        """
            Function to set robots position up and initialize the communication with 
            vision server  
        """


        super(GKStrategy, self).set_up()
        self.sock.sendto('', self.VISION_SERVER)


        #Array for Initial Position for each team, index 0 has red robot positions
        InitialPositions = [
            [
                RobotPosition(0, 0, 180),
                RobotPosition(50, 10, 180)
            ],
            [
                RobotPosition(0, 0, 0),
                RobotPosition(-50, -10, 0)
            ]
        ]
        #setting robot positions up
        self.goalkeeper_controller = Controller()
        #self.defensor_controller = Controller()


    def strategy(self, in_data_serialized):

            my_team = in_data_serialized.teams[self.team]
            ball = in_data_serialized.ball

            if self.team == RED_TEAM:
                goal = Position(-75, 0)
            else:
                goal = Position(75, 0)

            out_data = VsssOutData()

            out_data.moves.append(get_goalKeeper_move(self.team, my_team[0], 
                ball, goal, self.goalkeeper_controller))
            

        	#out_data.moves.append(get_defensor_move(self.team, my_team[1], ball, self.opposite_goal,
            #               self.defensor_controller))
            return out_data
        

if __name__ == '__main__':
    def help():
        return """./goalKeeperStrategy 0 = red team
        ./goalKeeperStrategy 1 = blue team      """

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    team = int(sys.argv[1])
    goalk_Strategy = GKStrategy(team, 1)
    goalk_Strategy.run()