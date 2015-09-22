#!/usr/bin/python

import socket
import sys
import time

from vsss.serializer import VsssSerializer, VsssOutData
from vsss.core import Move, Position, RED_TEAM, BLUE_TEAM
from vsss.utils import Controller, normalize

VISION_SERVER = ('', 9009)
CONTROL_SERVER = ('', 9009)
THIS_SERVER = ('', 9091)

prev_time = time.time() * 1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(SERVER)

sock.sendto('', VISION_SERVER)

def ball_to_center(player, ball, goal, controller):
    print('Ball to center')
    if player.distance_to(ball) < 5:
        if player.angle_to(goal) > 0:
            return Move(0, 20)
        else:
            return Move(0, -20)
    else:
        return controller.go_to_from(ball, player)

def go_to_shooting_pos(player, ball, goal, controller):
    print('go to shooting pos')
    if not abs(player.angle_to(goal) - ball.angle_to(goal)) < 0.2:
        vec_ball_to_del = goal.vector_to(ball) / goal.distance_to(ball)
        dest = ball.translate(vec_ball_to_del * 5)
        dest.theta = normalize(ball.angle_to(goal))
    else:
        dest = Position(player.x, player.y)
        dest.theta = player.angle_to(goal)
    return controller.go_to_from(dest, player)

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
    dest = Position(ball.x, ball.y)
    dest.theta = 90

    dest.y = min(16.5, max(-16.5, dest.y))
    if my_color == RED_TEAM:
        dest.x = 68
    else:
        dest.x = -68
    return controller.go_to_from(dest, player)


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

if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./player 0
        ./player 1"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_color = int(sys.argv[1])
    vsss_serializer = VsssSerializer(team_size=3, my_team=my_color)

    portero_controller = Controller()
    if my_color == RED_TEAM:
        delantero_controller = Controller(initial=Position(0, 0, 180))
        medio_controller = Controller(initial=Position(50, 10, 180))
    else:
        delantero_controller = Controller(initial=Position(0, 0, 0))
        medio_controller = Controller(initial=Position(-50, -10, 0))



    while True:
        in_data, addr = sock.recvfrom(1024)
        cur_time = time.time() * 1000 # milliseconds
        if cur_time - prev_time > 0:
            prev_time = cur_time
            data = vsss_serializer.load(in_data)

            my_team = data.teams[my_color]
            ball = data.ball

            if my_color == RED_TEAM:
                goal = Position(-75, 0)
            else:
                goal = Position(75, 0)

            out_data = VsssOutData()
            out_data.moves.append(get_portero_move(my_color, my_team[0], ball, goal, portero_controller))
            out_data.moves.append(get_medio_move(my_color, my_team[1], ball, goal, medio_controller))
            out_data.moves.append(get_delantero_move(my_color, my_team[2], ball, goal, delantero_controller))
            # out_data.moves.append(Move())

            out_data = vsss_serializer.dump(out_data)
            sock.sendto(out_data, CONTROL_SERVER)
