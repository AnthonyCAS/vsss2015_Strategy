import time
import math
from vsss.vsss_math.arithmetic import *
from vsss.colors import *

import sys
import pygame
from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
from vsss.move import Move
from vsss.visualizer import VsssVisualizer

listPredPositions = []
tam_prediction = 3

class PredictionBase(object):
    """
    params:
        n: max size of Buffer
        time_frame: average of buffer size by one second
    """
    def __init__(self, n=100, time_frame=30):
        self.t0 = time.time()
        self.N = n
        self.time_frame = time_frame
        # Buffer to hold the last N positions
        self.pos_buffer = []
        # Buffer to hold the times of the last N positions
        self.time_buffer = []

    def get_current_time(self, delay=0):
        return time.time()-self.t0-delay

    # Computes time interval by a delta parameter, if delta is 0 it computes  time value which has passed to store time_frame positions in the buffer the last iteration
    def get_delta_time(self, delta=0):
        return self.time_buffer[-1-delta] - self.time_buffer[
            -self.time_frame-delta]

    def get_velocity(self, interval, delta=0):
        return vector_to(
            self.pos_buffer[-self.time_frame-delta],
            self.pos_buffer[-1-delta]
            ) / interval

    def get_acceleration(self, current_velocity, interval):
        return vector_to(
            self.get_velocity(self.get_delta_time(1), delta=1), 
            current_velocity
            ) / interval

    def update(self, pos, delay):
        self.time_buffer.append(self.get_current_time(delay))        
        self.pos_buffer.append(pos.tonp())
        if len(self.pos_buffer) > self.N:
            del self.pos_buffer[0:10]
            del self.pos_buffer[0:10]   

    def predict(self, deta_time):
        raise NotImplementedError()

    def check_prediction():
        raise NotImplementedError()


class MyPrediction(PredictionBase):

    def predict(self, delta_time):        
        """
        Predict delta_time seconds in the future from the last update time
        """
        print 'starting'
        # print 'history: ', self.pos_buffer
        # print 'times: ', self.time_buffer
        print len(self.pos_buffer)        
        if len(self.pos_buffer) < self.time_frame or not self.check_motion():
            return self.pos_buffer[-1]
        delta_time = self.get_delta_time()
        # print 'DELTA', delta_time
        # print self.get_current_time()
        print 'last pos: ', self.pos_buffer[-1]            
        print 'oldest pos: ', self.pos_buffer[-self.time_frame]            
        print 'VELOCITY: ', self.get_velocity(delta_time)
        position = self.pos_buffer[-1] + delta_time * self.get_velocity(
            delta_time)
        print "PREDICTION New Position: ", position
        return position

    def check_motion(self):

        if distance(self.pos_buffer[-1], self.pos_buffer[-15]) < 3:
            return False
        return True

    def check_prediction(self, ballPosition):
        'here put validations such as is_collision and check_boundaries'

    def is_collision(self, objectOne, objectTwo, radius):
        distance = objectOne.distance_to(objectTwo)
        if distance <= 2 * radius:
            print (' Distance: ({},{}) to ({},{}) = {}'.format(
                objectOne.x, objectOne.y,
                objectTwo.x, objectTwo.y, 
                distance))
            return True
        return False
    
    def check_boundaries(self, position):
        if position.x > 75 or position.x < -75:
            return True
        if position.y > 65 or position.y < -65:
            return True
        return False

    """ 
    Method that compute the new future position when the ball hits and object              
    """
    def compute_next_position(self, vef, vtime, left, current_ball):
        pass        


new_pos = None
def prediction_test():

    class PredictionVisualizer(VsssVisualizer):
        def extra_visualize(self):
            global new_pos
            if new_pos == None:
                return                       
            print "old pos extra_visualize: ", new_pos                
            center = self.to_screen(
                Position(new_pos[0], new_pos[1])).tonp()
            print 'new pos extra_visualize: ', center
            pygame.draw.circle(self.screen, GREEN, center, 3, 3)
            
                                
    class Prediction(TeamStrategyBase):
        # Strategy server 
        THIS_SERVER = ('localhost', 9001)

        CONTROL_SERVER = ('localhost', 9009)
        VISION_SERVER = ('localhost', 9009)
        serializer_class = VsssSerializerSimulator
        visualizer_class = PredictionVisualizer
        do_visualize = True
        use_control = False
        print_iteration_time = False

        def set_up(self):
            super(Prediction, self).set_up()
            self.controller = Controller()
            self.predictor = MyPrediction(time_frame=15)

        def strategy(self, data):
            global new_pos, listPredPositions
            team = data.teams[self.team]
            ball = data.ball
            print 'Actual: ', ball
            new_pos = data.ball
            self.predictor.update(ball, 0.0)       
            new_pos = self.predictor.predict(1)            

            out_data = VsssOutData()
            return out_data


    my_color = 0
    strategy = Prediction(my_color, 3)
    strategy.run()


if __name__ == "__main__":
    prediction_test()
