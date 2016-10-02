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

MY_PORT = 9001

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

    def predict(self):
        raise NotImplementedError()

    def check_prediction():
        raise NotImplementedError()


class MyPrediction(PredictionBase):

    def predict(self):        
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
        # print 'POS[-1]: ', self.pos_buffer[-1]            
        # print 'POS[time_frame]: ', self.pos_buffer[-self.time_frame]         
        print 'VELOCITY: ', self.get_velocity(delta_time)
        current_velocity = self.get_velocity(delta_time)
        position = self.pos_buffer[-1] + delta_time * current_velocity - (
            delta_time*delta_time)*self.get_acceleration(
                current_velocity, delta_time) / 2
        print "PREDICTION: New Position: ", position
        return self.check_prediction(position)

    def check_motion(self):
        if distance(self.pos_buffer[-1], self.pos_buffer[-15]) < 3:
            return False
        return True

    # Method which check is there is collision 
    # or ball collides with other object
    def check_prediction(self, position):
        if self.check_boundaries(position):
            return self.compute_next_position(position)
        return position

    # we need positions of other objects like robots
    def is_collision(self, object_one, object_two, radius):
        distance = distance(object_one, object_two)
        if distance <= 2 * radius:
            print (' Distance: ({},{}) to ({},{}) = {}'.format(
                object_one.x, object_one.y,
                object_two.x, object_two.y, 
                distance))
            return True
        return False
    
    def check_boundaries(self, position):
        if position[0] > 75 or position[0] < -75:
            return True
        if position[1] > 65 or position[1] < -65:
            return True
        return False

    """ 
    Method that compute the new future position when the ball hits an object
    like wall
    """
    def compute_next_position(self, position):
        if position[0] > 75:
            position[0] = position[0] - 2*(position[0]-75)
        elif position[0] < -75:
            position[0] = position[0] - 2*(position[0]+75)
        elif position[1] > 65:
            position[1] = position[1] - 2*(position[1]-65)
        elif position[1] < -65:
            position[1] = position[1] - 2*(position[1]+65)
        return position     


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
            global MY_PORT
            if MY_PORT:
                THIS_SERVER = ('localhost', MY_PORT)
            super(Prediction, self).set_up()
            self.controller = Controller()
            self.predictor = MyPrediction(time_frame=15)

        def strategy(self, data):
            global new_pos
            team = data.teams[self.team]
            ball = data.ball
            print 'Actual Position: ({})'.format(
                ball.tonp())
            new_pos = data.ball
            self.predictor.update(ball, 0.0)       
            new_pos = self.predictor.predict()            

            out_data = VsssOutData()
            return out_data


    my_color = 0
    strategy = Prediction(my_color, 3)
    strategy.run()


if __name__ == "__main__":
    def help():
        return """
            You have to execute this script with the following format:
            ./prediction_one.py port-number
        """

    # Help the user if he doesn't know how to use the command
    print len(sys.argv)
    MY_PORT = 9001
    if len(sys.argv) == 2:
        MY_PORT = int(sys.argv[1])
    else:
        print help()
        sys.exit()


    prediction_test()
