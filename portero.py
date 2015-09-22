#!/usr/bin/python

import socket
import sys
import time

from vsss.serializer import VsssSerializer, VsssOutData
from vsss.core import Move
from vsss.utils import go_to_from

VISION_SERVER = ('', 9009)
CONTROL_SERVER = ('', 9009)
THIS_SERVER = ('', 9091)

prev_time = time.time() * 1000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(SERVER)

sock.sendto('', VISION_SERVER)




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
            player = my_team[0]

            out_data = VsssOutData()

            dest = in_data.ball
            dest.theta = 90

            dest.y = min(16.5, max(-16.5, dest.y))
            if sys.argv[1] == '0':
                dest.x = 68
            else:
                dest.x = -68
            move = go_to_from(dest, player)

            out_data.moves.append(move)
            out_data.moves.append(Move())
            out_data.moves.append(Move())

            out_data = vsss_serializer.dump(out_data)
            sock.sendto(out_data, CONTROL_SERVER)
