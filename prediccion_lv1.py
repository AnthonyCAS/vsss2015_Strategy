import sys
import pygame
import time
#from vsss_math import pi
import numpy as np

from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategyBase
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

# minimum distance
MD = 2

class PredictBall(object):
    def __init__(self):
        self.history = []
        self.times = []
        self.secondLastPosition = None
        self.lastPosition = None

    def update(self, ball, now):
        print ('current time: {}').format(now)
        #if len(self.history) <  2:
        self.history.append(ball)
        self.times.append(now)
        '''else:
            self.secondLastPosition = self.history[-2]
            self.lastPosition = self.history[-1]
            if self.lastPosition.distance_to(self.secondLastPosition) > MD:
                self.history.append(ball)
                self.times.append(now)'''

    def predict(self, future):
        listPredPositions = []
        if len(self.history) < 2 or future is None:
            #listPredPositions.append(Position(self.history[-1].x,self.history[-1].y))
            return [Position(self.history[-1].x,self.history[-1].y)]

        listPrediction = range(future)
    
        a = self.history[-2]
        b = self.history[-1]
        v = a.vector_to(b)
        at = self.times[-2]
        bt = self.times[-1]
        dt = bt-at

        for prediction in listPrediction :

            factor = prediction + 1 / dt
            #print 'factor: {}'.format(factor)
            ret = np.array([b.x, b.y]) + v*factor
            listPredPositions.append(Position(ret[0], ret[1]))
        return listPredPositions




class SimulatorVisionTestStrategy(TeamStrategyBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    VISION_SERVER = ('127.0.0.1', 9001)
    THIS_SERVER = ('127.0.0.1', 9002)
    CONTROL_SERVER = ('127.0.0.1', 9001)
    latency = 100
    do_predict = False
    serializer_class = VsssSerializerSimulator

    def set_up(self):
        super(SimulatorVisionTestStrategy, self).set_up()
        self.sock.sendto('', self.VISION_SERVER)
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

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYUP:
                self.do_predict = True
            if event.type == pygame.KEYDOWN:
                self.do_predict = False

        if self.do_predict:
            self.ballPositions = self.pred.predict(5)
            self.pred_time = time.time()

        if self.pred_time is None:
            pass
        elif time.time() - self.pred_time > 2:
            self.pred_time = None
        else:
            for bPosition in self.ballPositions :
                pygame.draw.circle(
                    screen, BLACK, [int(bPosition.x * enlargement), int(bPosition.y * enlargement)], 3
                )


        pygame.display.flip()

        return VsssOutData(moves=[Move(10, 10)])

    def tear_down(self):
        super(SimulatorVisionTestStrategy, self).tear_down()
        pygame.quit()


if __name__ == '__main__':
    strategy = SimulatorVisionTestStrategy(0, 1)

    strategy.run()
