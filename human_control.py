import sys
import pygame
from pygame.locals import *

from vsss.serializer import VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move


class HumanControlStrategy(TeamStrategyBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    latency = 200
    use_vision = False
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.111', 9003)

    serializer_class = VsssSerializerReal

    def set_up(self):
        super(HumanControlStrategy, self).set_up()
        assert (self.team_size <= 3)
        print "Pygame init"
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))

    def strategy(self, data):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.done = True

        controls = [
            [K_UP, K_DOWN, K_RIGHT, K_LEFT],
            [K_w, K_s, K_d, K_a],
            [K_i, K_k, K_l, K_j]
        ]

        moves = []
        for i in range(self.team_size):
            move = Move(0, 0)
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
        out_data = VsssOutData(moves=moves)
        return out_data


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
