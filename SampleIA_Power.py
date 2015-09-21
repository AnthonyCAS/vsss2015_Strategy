#!/usr/bin/python

import socket
import sys
import time

from vsss.strategy import TeamStrategyBase
from vsss.settings import *

from vsss.serializer import VsssSerializerSimulator
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
#from vsss.servers import *

THIS_SERVER = ('', 9091)
temp_serializer = None
VISION_SERVER = ('', 9009)
CONTROL_SERVER = ('', 9009)

def ball_to_center(player, ball, goal, controller):
    print('Ball to center')
    if player.distance_to(ball) < 5:
        if player.angle_to(goal) > 0:
            return Move(0, 20)
        else:
            return Move(0, -20)
    else:
        return controller.go_to_from(ball, player, 'pow')

def go_to_shooting_pos(player, ball, goal, controller):
    print('go to shooting pos')
    if not abs(player.angle_to(goal) - ball.angle_to(goal)) < 0.2:
        vec_ball_to_del = goal.vector_to(ball) / goal.distance_to(ball)
        dest = ball.translate(vec_ball_to_del * 5)
        dest.theta = normalize_angle(ball.angle_to(goal))
    else:
        dest = Position(player.x, player.y)
        dest.theta = player.angle_to(goal)
    return controller.go_to_from(dest, player, 'pow')

def shoot(player, ball, goal, controller):
    print('shoot')
    move = controller.go_to_from(goal, player, speed=75)
    return move

def idle(player, ball, goal, controller):
    print('idle')
    return controller.go_to_from(controller.initial, player)



class PlayerState:
    def __init__(self, state):
        self.state = state

    def get_move(self, player, ball, goal, controller):
        return self.state(player, ball, goal, controller)


def get_portero_move(my_color, player, ball, goal, controller):
    dest = RobotPosition(ball.x, ball.y)
    dest.theta = 90

    dest.y = min(16.5, max(-16.5, dest.y))
    if my_color == RED_TEAM:
        dest.x = 68
    else:
        dest.x = -68
    return controller.go_to_from(dest, player, 'pow')


delantero_state = PlayerState(go_to_shooting_pos)
def get_delantero_move(my_color, player, ball, goal, controller):
    if abs(goal.x - ball.x) < 80:
        if abs(ball.y) > 60 or abs(ball.x) > 70:
            delantero_state.state = ball_to_center
        elif (abs(player.angle_to(goal) - ball.angle_to(goal)) < 1 and
                      player.distance_to(goal) > ball.distance_to(goal)):
            delantero_state.state = shoot
        else:
            delantero_state.state = go_to_shooting_pos
    else:
        delantero_state.state = idle

    move = delantero_state.get_move(player, ball, goal, controller)
    return move


medio_state = PlayerState(go_to_shooting_pos)
def get_medio_move(my_color, player, ball, goal, controller):
    if abs(goal.x - ball.x) > 80:
        if abs(ball.y) > 60 or abs(ball.x) > 70:
            medio_state.state = ball_to_center
        elif (abs(player.angle_to(goal) - ball.angle_to(goal)) < 1 and
                      player.distance_to(goal) > ball.distance_to(goal)):
            medio_state.state = shoot
        else:
            medio_state.state = go_to_shooting_pos
    else:
        medio_state.state = idle

    move = medio_state.get_move(player, ball, goal, controller)
    return move

class Test_strategy(TeamStrategyBase):

    def __init__(self, team, team_size):
        self.VISION_SERVER = VISION_SERVER        
        self.CONTROL_SERVER = CONTROL_SERVER      
        self.THIS_SERVER = THIS_SERVER  
        self.serializer = temp_serializer
        super(Test_strategy, self).__init__(team, team_size)

    def set_up(self):
        """
            Function to set robots position up and initialize the communication with 
            vision server  
        """
        self.sock.sendto('', self.VISION_SERVER)
        self.goalkeeper_controller = Controller()
        if self.team == RED_TEAM:
            self.forward_controller = Controller(initial=Position(0, 0, 180))
            self.defence_controller = Controller(initial=Position(50, 10, 180))
        else:
            self.forward_controller = Controller(initial=Position(0, 0, 0))
            self.defence_controller = Controller(initial=Position(-50, -10, 0))

    def strategy(self, in_data_serialized):

            my_team = in_data_serialized.teams[self.team]
            ball = in_data_serialized.ball

            if self.team == RED_TEAM:
                goal = Position(-75, 0)
            else:
                goal = Position(75, 0)

            out_data = VsssOutData()
            out_data.moves.append(get_portero_move(self.team, my_team[0], 
                ball, goal, self.goalkeeper_controller))
            out_data.moves.append(get_medio_move(self.team, my_team[1], 
                ball, goal, defence_controller))
            out_data.moves.append(get_delantero_move(self.team, my_team[2], 
                ball, goal, forward_controller))
            
            return out_data
        

if __name__ == '__main__':
    def help():
        return """./SampleIA_Power 0 = red team
        ./SampleIA_Power 1 = blue team      """

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    team = int(sys.argv[1])
    temp_serializer = VsssSerializerSimulator(team,3)
    hardplay = Test_strategy(team, 3)
    hardplay.run()