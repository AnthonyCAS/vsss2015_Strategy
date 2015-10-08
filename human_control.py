import sys
import pygame
import time
from pygame.locals import *

from vsss.serializer import VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move


class HumanControlStrategy(TeamStrategyBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    latency = 200
    use_vision = False
    THIS_SERVER = ('0.0.0.0', 9004)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerReal

    def set_up(self):
        super(HumanControlStrategy, self).set_up()
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))
        self.prev_send = time.time() * 1000

    def strategy(self, data):
        send_now = False

        events = pygame.event.get()
        for event in events:
            if event.type == KEYDOWN or event.type == KEYUP:
                send_now = True

        if time.time()*1000 - self.prev_send > 200:
            send_now = True

        if send_now:
            self.prev_send = time.time()*1000
            move = Move(0, 0)
            if pygame.key.get_pressed()[K_UP]:
                move.linvel = 1
            if pygame.key.get_pressed()[K_DOWN]:
                move.linvel = -1
            if pygame.key.get_pressed()[K_RIGHT]:
                move.angvel = 0.5
            if pygame.key.get_pressed()[K_LEFT]:
                move.angvel = -0.5
        else:
            move = Move(10,10)

        if send_now:
            print move
        out_data = VsssOutData(moves=[move])
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
    strategy = HumanControlStrategy(my_color, 1)
    strategy.run()
