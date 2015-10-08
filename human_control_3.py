import sys
import pygame
from pygame.locals import *

from vsss.serializer import VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move


class HumanControlStrategy(TeamStrategyBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    latency = 50
    use_vision = False
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerReal

    def setup(self):
        super(HumanControlStrategy, self).setup()
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))

    def strategy(self, data):
        move = Move(0, 0)
        if pygame.key.get_pressed()[K_UP]:
            move.linvel = 1
        if pygame.key.get_pressed()[K_DOWN]:
            move.linvel = -1
        if pygame.key.get_pressed()[K_RIGHT]:
            move.angvel = 0.5
        if pygame.key.get_pressed()[K_LEFT]:
            move.angvel = -0.5

        move2 = Move(0, 0)
        if pygame.key.get_pressed()[K_w]:
            move2.linvel = 1
        if pygame.key.get_pressed()[K_s]:
            move2.linvel = -1
        if pygame.key.get_pressed()[K_d]:
            move2.angvel = 0.5
        if pygame.key.get_pressed()[K_a]:
            move2.angvel = -0.5

        move3 = Move(0, 0)
        if pygame.key.get_pressed()[K_i]:
            move3.linvel = 1
        if pygame.key.get_pressed()[K_k]:
            move3.linvel = -1
        if pygame.key.get_pressed()[K_l]:
            move3.angvel = 0.5
        if pygame.key.get_pressed()[K_j]:
            move3.angvel = -0.5

        print move, move2, move3
        out_data = VsssOutData(moves=[move, move2, move3])
        pygame.event.pump()
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
