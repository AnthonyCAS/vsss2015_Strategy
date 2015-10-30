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


def spin_to_repel(player, ball, goal, controller, *args, **kwargs):
    A = player.angle_to(goal)
    B = player.angle_to(ball)
    counter_clock = arclen_ori(A, B, 1.0, 1)
    clock = arclen_ori(A, B, 1.0, -1)
    if clock < counter_clock:
        return Move(0, -1)
    else:
        return Move(0, 1)

def shoot(player, ball, goal, controller, *args, **kwargs):
    next = RobotPosition(ball.x, ball.y, ball.angle_to(goal))
    move = controller.go_with_trajectory(next, player, 10.0)
    return move

def idle(player, ball, goal, controller, *args, **kwargs):
    print('idle')
    initial = kwargs["initial"]
    follow_ball = Position(initial.x, ball.y)
    return controller.go_with_trajectory(initial, player, 10.0)



class PlayerState:
    def __init__(self, state):
        self.state = state

    def get_move(self, player, ball, goal, controller, *args, **kwargs):
        return self.state(player, ball, goal, controller, *args, **kwargs)


def get_portero_move(my_color, player, ball, goal, controller, *args, **kwargs):
    dest = Position(ball.x, ball.y)

    dest.y = min(16.5, max(-16.5, dest.y))
    if my_color == RIGHT_TEAM:
        dest.x = 68
    else:
        dest.x = -68
    return controller.go_to_from(dest, player)


delantero_state = PlayerState(idle)
def get_delantero_move(my_color, player, ball, goal, controller, *args, **kwargs):
    if abs(goal.x - ball.x) < 80:
        delantero_state.state = shoot
    else:
        delantero_state.state = idle

    move = delantero_state.get_move(player, ball, goal, controller, *args, **kwargs)
    return move


medio_state = PlayerState(idle)
def get_medio_move(my_color, player, ball, goal, controller, *args, **kwargs):
    if abs(goal.x - ball.x) > 80:
        medio_state.state = shoot
    else:
        medio_state.state = idle

    move = medio_state.get_move(player, ball, goal, controller, *args, **kwargs)
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

        if my_color == RED_TEAM:
            self.delantero_initial=RobotPosition(0, 0, 180)
            self.medio_initial = RobotPosition(50, 10, 180)
            self.portero_initial = RobotPosition(71, 0, 0)
        else:
            self.delantero_initial=RobotPosition(0, 0, 0)
            self.medio_initial = RobotPosition(-50, -10, 0)
            self.portero_initial = RobotPosition(-71, 0, 0)


    def strategy(self, data):
        my_team = data.teams[my_color]
        ball = data.ball

        if self.team == RED_TEAM:
            goal = Position(-75, 0)
        else:
            goal = Position(75, 0)

        out_data = VsssOutData()
        out_data.moves.append(get_portero_move(
            my_color, my_team[0], ball, goal, self.portero_controller,
            initial=self.portero_initial))
        out_data.moves.append(get_medio_move(
            my_color, my_team[1], ball, goal, self.medio_controller,
            initial=self.medio_initial))
        out_data.moves.append(get_delantero_move(
            my_color, my_team[2], ball, goal, self.delantero_controller,
            initial=self.delantero_initial))
        # out_data.moves.append(Move())
        return out_data


if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./script_name 0 9002
        ./script_name 1 9004"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 3:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_color = int(sys.argv[1])
    strategy = VeryFirstStrategy(my_color, 3, this_server=("0.0.0.0", int(sys.argv[2])))

    strategy.run()
