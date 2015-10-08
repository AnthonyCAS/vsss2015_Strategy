import pygame
import math
import numpy as np

from vsss.position import RobotPosition

def hermite(t, P=np.array([0, 4]), Q=np.array([2,5]), V=np.array([0, 500]), W=np.array([500, 0])):
    return P*math.pow(1-t, 2) * (2*t+1) + Q*math.pow(t, 2)*(-2*t+3) + V*t*math.pow(t-1, 2) + W*(t-1)*math.pow(t,2)

class Trajectory(object):
    def get_trajectory(self, goal, current):
        """
        Return a set of intermediate points
        :param goal: RobotPosition where we want to go
        :param current: RobotPosition where we are now
        :return: List of intermediate points
        """
        ret = []
        for t in np.arange(0, 1, 0.1):
            P = current.to_numpy()
            Q = goal.to_numpy()
            V = current.theta_to_speed()
            W = goal.theta_to_speed()
            ret.append(hermite(t, P=P, Q=Q, V=V, W=W))
        return ret
