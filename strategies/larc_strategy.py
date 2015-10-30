#!/usr/bin/python
import sys
import os

path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(path), "../"))

import socket
import time

from vsss.serializer import VsssSerializerSimulator, VsssOutData
from vsss.move import Move
from vsss.position import Position, RobotPosition
from vsss.settings import RED_TEAM, BLUE_TEAM, LEFT_TEAM, RIGHT_TEAM
from vsss.controller import Controller
from vsss.vsss_math.angles import normalize
from vsss.vsss_math.arithmetic import *


my_side = 0


def spin_to_repel(player, ball, goal, controller, initial):
    A = player.angle_to(goal)
    B = player.angle_to(ball)
    counter_clock = arclen_ori(A, B, 1.0, 1)
    clock = arclen_ori(A, B, 1.0, -1)
    if clock < counter_clock:
        return Move(0, -1)
    else:
        return Move(0, 1)


def portero_follow_ball_y_axis(player, ball, goal, controller, initial):
    if my_side == 0:
        x = -68.0
    else:
        x = 68.0
    follow_ball = Position(x, min(18, max(-18, ball.y)))
    return controller.go_to_from(follow_ball, player)


def shoot(player, ball, goal, controller, initial):
    next = RobotPosition(ball.x, ball.y, ball.angle_to(goal))
    move = controller.go_with_trajectory(next, player)
    return move


def idle(player, ball, goal, controller, initial):
    return Move(0,0)

def go_to_initial(player, ball, goal, controller, initial):
    return controller.go_with_trajectory(initial, player)



class PlayerState:
    def __init__(self, state):
        self.state = state

    def get_move(self, player, ball, goal, controller, initial):
        return self.state(player, ball, goal, controller, initial)


portero_state = PlayerState(idle)
def get_portero_move(my_side, player, ball, goal, controller, initial):
    dist = player.distance_to(ball)
    if player.distance_to(goal) > 20:
        portero_state.state = go_to_initial
    elif dist > 50:
        portero_state.state = idle
    elif dist <= 8:
        portero_state.state = spin_to_repel
    else:
        portero_state.state = portero_follow_ball_y_axis
    return portero_state.get_move(player, ball, goal, controller, initial)


delantero_state = PlayerState(idle)
def get_delantero_move(my_side, player, ball, goal, controller, initial):
    if abs(goal.x - ball.x) < 80:
        delantero_state.state = shoot
    else:
        delantero_state.state = idle

    move = delantero_state.get_move(player, ball, goal, controller, initial)
    return move


medio_state = PlayerState(idle)
def get_medio_move(my_side, player, ball, goal, controller, initial):
    if abs(goal.x - ball.x) > 80:
        medio_state.state = shoot
    else:
        medio_state.state = idle

    move = medio_state.get_move(player, ball, goal, controller, initial)
    return move



from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase


class VeryFirstStrategy(TeamStrategyBase):
    use_control = True
    do_visualize = True
    use_vision = True
    latency = 50
    print_iteration_time = False

    CONTROL_SERVER = ('127.0.0.1', 9003)

    serializer_class = VsssSerializerSimulator
    def set_up(self):
        super(VeryFirstStrategy, self).set_up()
        self.portero_controller = Controller()
        self.medio_controller = Controller()
        self.delantero_controller = Controller()

        if my_side == LEFT_TEAM:
            self.delantero_initial=RobotPosition(0, 0, 0)
            self.medio_initial = RobotPosition(-50, -10, 0)
            self.portero_initial = RobotPosition(-71, 0, 0)
        else:
            self.delantero_initial=RobotPosition(0, 0, 180)
            self.medio_initial = RobotPosition(50, 10, 180)
            self.portero_initial = RobotPosition(71, 0, 0)


    def strategy(self, data):
        my_team = data.teams[my_side]
        ball = data.ball

        if self.team == RED_TEAM:
            goal = Position(-75, 0)
        else:
            goal = Position(75, 0)

        out_data = VsssOutData()
        out_data.moves.append(get_portero_move(
            my_side, my_team[0], ball, goal, self.portero_controller,
            initial=self.portero_initial))
        out_data.moves.append(Move())
        out_data.moves.append(Move())
        # out_data.moves.append(get_medio_move(
        #     my_side, my_team[1], ball, goal, self.medio_controller,
        #     initial=self.medio_initial))
        # out_data.moves.append(get_delantero_move(
        #     my_side, my_team[2], ball, goal, self.delantero_controller,
        #     initial=self.delantero_initial))
        return out_data


if __name__ == '__main__':
    strategy = VeryFirstStrategy(my_side, 3, this_server=("0.0.0.0", 9002))

    strategy.run()
