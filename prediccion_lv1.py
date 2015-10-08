import sys
import pygame
import time
from math import pi
import numpy as np

from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategySimulatorBase, TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move
from vsss.position import Position


# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

# Set the height and width of the screen
field_size = [150, 130]
enlargement = 3
screen_size = map(lambda x: x*enlargement, field_size)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Test vision")


class PredictBall(object):
    def __init__(self):
        self.history = []
        self.times = []

    def update(self, ball, now):
        print now
        self.history.append(ball)
        self.times.append(now)

    def predict(self, future):
        if len(self.history) < 2 or future is None:
            return Position(0,0)
        a = self.history[-2]
        b = self.history[-1]
        v = a.vector_to(b)
        at = self.times[-2]
        bt = self.times[-1]
        dt = bt-at
        factor = future/dt
        print 'factor', factor
        ret = np.array([b.x, b.y]) + v*factor
        return Position(ret[0], ret[1])




class SimulatorVisionTestStrategy(TeamStrategySimulatorBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    VISION_SERVER = ('0.0.0.0', 9001)
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 8003)
    latency = 100

    serializer_class = VsssSerializerSimulator

    def set_up(self):
        super(SimulatorVisionTestStrategy, self).set_up()
        pygame.init()
        self.pred = PredictBall()
        self.pred_time = None

    def strategy(self, data):
        screen.fill(WHITE)
        ball = data.ball
        ball.x += 75
        ball.y = -ball.y
        ball.y += 65

        self.pred.update(ball, time.time())

        pygame.draw.circle(
            screen, RED, [int(ball.x * enlargement), int(ball.y * enlargement)], int(2.2*enlargement)
        )

        do_predict = False
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYUP:
                do_predict = True

        if do_predict:
            self.pball = self.pred.predict(2)
            self.pred_time = time.time()

        if self.pred_time is None:
            pass
        elif time.time() - self.pred_time > 2:
            self.pred_time = None
        else:
            pygame.draw.circle(
                screen, BLACK, [int(self.pball.x * enlargement), int(self.pball.y * enlargement)], 3
            )


        pygame.display.flip()

        return VsssOutData(moves=[Move(10, 10)])

    def tear_down(self):
        super(SimulatorVisionTestStrategy, self).tear_down()
        pygame.quit()


if __name__ == '__main__':
    strategy = SimulatorVisionTestStrategy(0, 1)

    strategy.run()
