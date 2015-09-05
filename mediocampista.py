#!/usr/bin/python

import socket
import sys
import time

from utils.serializer import VsssSerializer, VsssOutData
from utils.core import Move, Position
from utils.utils import go_to_from, normalize_angle

VISION_SERVER = ('', 9009)
CONTROL_SERVER = ('', 9009)
THIS_SERVER = ('', 9091)

prev_time = time.time() * 1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(SERVER)

sock.sendto('', VISION_SERVER)


def go_to_shooting_pos(player, ball, goal):
    print('go to shooting pos')
    if not abs(player.angle_to(goal) - ball.angle_to(goal)) < 5:
        vec_ball_to_del = goal.vector_to(ball) / goal.distance_to(ball)
        dest = ball.translate(vec_ball_to_del * 15)
        dest.theta = normalize_angle(ball.angle_to(goal))
    else:
        dest = player
        dest.theta = player.angle_to(goal)
    return go_to_from(dest, player)


def shoot(player, ball, goal):
    print('shoot')
    move = go_to_from(ball, player, speed=75)
    return move

def idle(player, ball, goal):
    print('idle')
    return Move(0, 0)



class PlayerState:
    def __init__(self, state):
        self.state = state

    def get_move(self, player, ball, goal):
        return self.state(player, ball, goal)



player_state = PlayerState(go_to_shooting_pos)

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


    while True:
        in_data, addr = sock.recvfrom(1024)
        cur_time = time.time() * 1000 # milliseconds
        if cur_time - prev_time > 50:
            prev_time = cur_time
            in_data = vsss_serializer.load(in_data)

            my_team = in_data.teams[my_color]
            player = my_team[2]
            ball = in_data.ball

            out_data = VsssOutData()

            if sys.argv[1] == '0':
                goal = Position(-75, 0)
            else:
                goal = Position(75, 0)

            if ball.distance_to(goal) > 70:
                if abs(player.angle_to(goal) - ball.angle_to(goal)) < 5:
                    player_state.state = shoot
                else:
                    player_state.state = go_to_shooting_pos
            else:
                player_state.state = idle

            move = player_state.get_move(player, ball, goal)

            out_data.moves.append(Move())
            out_data.moves.append(Move())
            out_data.moves.append(move)

            out_data = vsss_serializer.dump(out_data)
            sock.sendto(out_data, CONTROL_SERVER)
