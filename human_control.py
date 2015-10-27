import sys
import pygame
from pygame.locals import *

from vsss.serializer import VsssSerializerReal, VsssSerializerSimulator
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move
import time


class HumanControlStrategy(TeamStrategyBase):
    latency = 50
    own_latency = 100
    use_vision = False
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerReal

    def set_up(self):
        super(HumanControlStrategy, self).set_up()
        assert (self.team_size <= 3)
        pygame.init()
        self.screen = pygame.display.set_mode((100, 100))
        self.prev_send = time.time()
        self.power = 1.0

    def strategy(self, data):
        send_now = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN or e.type == pygame.KEYUP:
                send_now = True
                if e.key == pygame.K_ESCAPE:
                    self.done = True
                elif e.key >= pygame.K_0 and e.key <= pygame.K_9:
                    self.power = (e.key - pygame.K_0)/10.0
                    if self.power == 0:
                        self.power = 1.0

        if time.time() - self.prev_send > self.own_latency/1000.0:
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
            move = Move(0, 0)
            if pygame.key.get_pressed()[controls[i][0]]:
                move.linvel = self.power
            if pygame.key.get_pressed()[controls[i][1]]:
                move.linvel = -self.power
            if pygame.key.get_pressed()[controls[i][2]]:
                move.angvel = self.power
            if pygame.key.get_pressed()[controls[i][3]]:
                move.angvel = -self.power
            moves.append(move)
            print move,

        print ''
        self.prev_send = time.time()
        return VsssOutData(moves=moves)


if __name__ == '__main__':
    my_color = 0
    strategy = HumanControlStrategy(my_color, 3)
    strategy.run()
