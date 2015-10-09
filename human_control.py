import sys
import pygame
from pygame.locals import *

from vsss.serializer import VsssSerializerReal, VsssSerializerSimulator
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move
from vsss.utils import get_millis


class HumanControlStrategy(TeamStrategyBase):
    latency = 50
    own_latency = 200
    use_vision = False
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.147', 9003)

    serializer_class = VsssSerializerReal

    def set_up(self):
        super(HumanControlStrategy, self).set_up()
        assert (self.team_size <= 3)
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))
        self.prev_send = get_millis()

    def strategy(self, data):
        send_now = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
                send_now = True
                if e.key == pygame.K_ESCAPE:
                    self.done = True

        if get_millis() - self.prev_send > self.own_latency:
            send_now = True

        if not send_now:
            return VsssOutData(moves=[Move()]*self.team_size)

        controls = [
            [K_UP, K_DOWN, K_RIGHT, K_LEFT],
            [K_w, K_s, K_d, K_a],
            [K_i, K_k, K_l, K_j]
        ]

        moves = []
        for i in range(self.team_size):
            move = Move(1, 1)
            if pygame.key.get_pressed()[controls[i][0]]:
                move.linvel = 1
            if pygame.key.get_pressed()[controls[i][1]]:
                move.linvel = -1
            if pygame.key.get_pressed()[controls[i][2]]:
                move.angvel = 0.5
            if pygame.key.get_pressed()[controls[i][3]]:
                move.angvel = -0.5
            moves.append(move)
            print move,

        print ''
        self.prev_send = get_millis()
        return VsssOutData(moves=moves)


if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./vision_test 0
        ./vision_test 1"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_color = int(sys.argv[1])
    strategy = HumanControlStrategy(my_color, 3)
    strategy.run()
