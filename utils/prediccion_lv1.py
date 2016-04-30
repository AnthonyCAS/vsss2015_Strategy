import sys
import pygame
import time
#from vsss_math import pi
import numpy as np
import math
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
# List of Positions
listPredPositions = []
tam_prediction = 5

class PredictBall(object):
    def __init__(self):
        self.history = []
        self.times = []
        self.prev_velocity = None
        self.tempPosition = []

    def update(self, ball, now):
        #print ('current time: {}').format(now)
        #if len(self.history) <  2:
        self.history.append(ball)
        self.times.append(now)
        if len(self.history) > 20:
            del self.history[0:10]
            del self.times[0:10]            
        '''else:
            self.secondLastPosition = self.history[-2]
            self.lastPosition = self.history[-1]
            if self.lastPosition.distance_to(self.secondLastPosition) > MD:
                self.history.append(ball)
                self.times.append(now)'''

    def is_collision(self, objectOne, objectTwo, radius):
        if objectOne.distance_to(objectTwo) <= 2 * radius:
            print ('distance: POS1 {},{} = {}'.format(objectOne.x, objectOne.y, objectOne.distance_to(objectTwo)))
            print ('distance: POS2 {},{} '.format(objectTwo.x, objectTwo.y ))
            return True
        return False
    
    def check_boundaries(self, position):
        if position.x > 75 or position.x < -75:
            return True
        if position.y > 65 or position.y < -65:
            return True
        return False

    def check_prediction(self, ballPosition):
        global listPredPositions
        if len(listPredPositions) > 0 and self.is_collision(listPredPositions[0], ballPosition, 2):
            del listPredPositions[0]
            return True
        return False


    def get_acceleration(self, dts, positions, ball):
        
        vel_tick = []
        prev_pos_x = ball[0]
        prev_pos_y = ball[1]
        for po, time in zip(positions, dts):
            temp = [(po.x - prev_pos_x) / time, (po.y - prev_pos_y) / time]
            print ('dts: {}').format(temp)
            vel_tick.append( math.sqrt(math.pow(temp[0],2) + math.pow(temp[1],2)) )
            prev_pos_x = po.x
            prev_pos_y = po.y
        
        acel_prom = 0
        aceleracion = []
        prev_velocity = 0
        for vel in vel_tick:
            if acel_prom == 0:
                aceleracion.append(vel)
                prev_velocity = vel
                continue
            aceleracion.append(vel - prev_velocity)
            acel_prom += vel - prev_velocity
            prev_velocity = vel

        return acel_prom, aceleracion


    '''
    pos1 and pos2 are postition object 
    return a velocity vector 
    '''
    def get_Velocity(self, pos1, pos2, time):
        return pos1.vector_to(pos2)  / time 

    def compute_next_poss(self, vef, vtime, left, current_ball):
        vvel = np.array([vef[0], vef[1]]) - np.array([self.prev_velocity[0], self.prev_velocity[1]])
        aceleracion = vvel / vtime
        lis = []
        for i in range(left):

            secondLastPo = self.history[-(i+2)]
            lastPo = self.history[-(i+1)]
            velocity_tick = lastPo.vector_to(secondLastPo)
            secondLastT = self.times[-(i+2)]
            lastT = self.times[-(i+1)]
            
            atime = lastT - secondLastT
            tick_pos = 0.5*math.pow(atime,2) * aceleracion + self.get_Velocity(secondLastPo, lastPo, atime) + np.array([lastPo.x, lastPo.y])
            print ('New pos: {}').format(tick_pos)
            pos = Position(tick_pos[0], tick_pos[1])
            #if self.check_boundaries(pos) == False and self.is_collision(pos, current_ball, 2) == False:
            lis.append(pos)
            #else:
            #    break
        return lis


    def predict_by_time(self, current_ball, time):
        global listPredPositions
        print ('Printing ball: {}, {}. {}').format(current_ball.x, current_ball.y,
            len(listPredPositions))
        if len(self.history) < 9:
            return self.tempPosition
        
        a = self.history[-2]
        b = self.history[-1]
        at = self.times[-2]
        bt = self.times[-1]
        
        atime = bt - at
        new_pos = self.get_Velocity(a, b, atime) + np.array([b.x, b.y])
        vf = self.get_Velocity(a, b, atime)
        vvf = np.array([b.x, b.y]) - np.array([a.x, a.y])
        
        aceleracion = vvf / atime


        if len(listPredPositions) == 0:
            pos = Position(new_pos[0], new_pos[1])

            secondLastPo = self.history[-4]
            lastPo = self.history[-3]
            velocity_temp = lastPo.vector_to(secondLastPo)
            secondLastT = self.times[-4]
            lastT = self.times[-3]

            atime = lastT - secondLastT
            future_pos =  np.array([b.x, b.y]) + 0.5*aceleracion * 4*4 
            print ('New pos 1: {}, time: {}').format(future_pos, atime)

            pos = Position(future_pos[0], future_pos[1])
            if self.check_boundaries(pos) == False and self.is_collision(pos, current_ball, 2) == False:
                listPredPositions.append(pos)
            
        else:
            print ('Pred: {}. {}').format(listPredPositions[0].x, listPredPositions[0].y)
            self.check_prediction(current_ball)
        self.prev_velocity = vf
        return []
            

    def predict(self, current_ball, times):
        global listPredPositions
        print ('Printing ball: {}, {}. {}').format(current_ball.x, current_ball.y,
            len(listPredPositions))
        if len(self.history) < 4:# or self.is_collision(current_ball, self.history[-1], 1):
            return self.tempPosition
            #listPredPositions.append(Position(self.history[-1].x,self.history[-1].y))
            #return [Position(self.history[-1].x,self.history[-1].y)]
        
        a = self.history[-2]
        b = self.history[-1]
        at = self.times[-2]
        bt = self.times[-1]
        
        atime = bt - at
        new_pos = self.get_Velocity(a, b, atime) + np.array([b.x, b.y])
        vf = self.get_Velocity(a, b, atime)
        print ('New pos: {}, time: {}').format(new_pos, atime)

        if len(listPredPositions) == 0:
            pos = Position(new_pos[0], new_pos[1])
            if self.check_boundaries(pos) == False and self.is_collision(pos, current_ball, 2) == False:
                listPredPositions.append(pos)
    
        else:

            self.tempPosition = self.compute_next_poss(vf, atime, tam_prediction - len(listPredPositions), current_ball)

            print ('Pred: {}. {}').format(listPredPositions[0].x, listPredPositions[0].y)
            if self.check_prediction(current_ball):
                self.tempPosition = []

        self.prev_velocity = vf
        return self.tempPosition

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
        #ball.x += 75
        #ball.y = -ball.y
        #ball.y += 65

        self.pred.update(ball, time.time())

        pygame.draw.circle(
            screen, RED, [int((ball.x + 75) * enlargement), int((-ball.y + 65) * enlargement)], int(2.2*enlargement)
        )

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYUP:
                self.do_predict = True
            if event.type == pygame.KEYDOWN:
                self.do_predict = False


        if self.do_predict:
            self.predPos = self.pred.predict(ball, 2)
            self.pred_time = time.time()

        if self.pred_time is None:
            pass
        elif time.time() - self.pred_time > 2:
            self.pred_time = None
        else:
            for i, bPosition in enumerate(listPredPositions) :
                col = BLACK
                if i == 0:
                    col = GREEN
                pygame.draw.circle(
                    screen, col, [int((bPosition.x + 75) * enlargement), int((-bPosition.y + 65) * enlargement)], 3
                )
            if len(self.predPos) != 0:

                for pre in self.predPos :
                
                    pygame.draw.circle(
                        screen, BLACK, [int((pre.x + 75) * enlargement), int((-pre.y + 65) * enlargement)], 3
                    )



        pygame.display.flip()

        return VsssOutData(moves=[Move(10, 10)])

    def tear_down(self):
        super(SimulatorVisionTestStrategy, self).tear_down()
        pygame.quit()


if __name__ == '__main__':
    strategy = SimulatorVisionTestStrategy(0, 1)

    strategy.run()
