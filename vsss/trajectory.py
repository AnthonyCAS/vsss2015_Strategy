import math
import numpy as np


def hermite(t, P=np.array([0, 4]), Q=np.array([2,5]), V=np.array([0, 500]), W=np.array([500, 0])):
    return P*(1-t)**2 * (2*t+1) + Q*t*t*(-2*t+3) + V*t*(t-1)**2 + W*(t-1)*t*t

def hermite_vel(t, P=np.array([0, 4]), Q=np.array([2,5]), V=np.array([0, 500]), W=np.array([500, 0])):
    return P*6*t*(t-1) - Q*6*t*(t-1) + V*(3*t**2 - 4*t + 1) + W*t*(3*t - 2)

class Trajectory(object):
    def __init__(self, init_speed = 100, final_speed=100):
        self.init_speed = init_speed
        self.final_speed = final_speed
        self.prev_point = None
        self.prev_vel = None

    def get_trajectory(self, goal, current, intermediate_points=10):
        """
        Return a set of intermediate points
        :param goal: RobotPosition where we want to go
        :param current: RobotPosition where we are now
        :return: List of intermediate points
        """
        dist = goal.distance_to(current)
        if dist < 10:
            self.prev_point = None
            self.prev_vel = None
            return [current.to_numpy(), goal.to_numpy()]
        ret = []
        if self.prev_point is None:
            P = current.to_numpy()
            V = current.theta_to_speed(dist*5)
            W = goal.theta_to_speed(dist*5)
        else:
            P = self.prev_point
            V = self.prev_vel
            W = self.prev_final_vel
            ret.append(current.to_numpy())

        Q = goal.to_numpy()

        step = 1.0/(intermediate_points+1)
        # print 'int', intermediate_points
        prev_gotten = False
        for t in np.arange(0, 1, step):
            p = hermite(t, P=P, Q=Q, V=V, W=W)
            ret.append(p)
            if not prev_gotten and np.linalg.norm(p-current.to_numpy()) > 10:
                prev_gotten = True
                self.prev_point = p
                self.prev_vel = (1-t)*hermite_vel(t, P=P, Q=Q, V=V, W=W)
                self.prev_final_vel = (1-t)*W
        if not prev_gotten:
            self.prev_point = None
            self.prev_vel = None
        ret.append(goal.to_numpy())
        return ret

if __name__ == "__main__":
    import pygame
    from colors import *
    from position import RobotPosition

    goal = RobotPosition(700,500,0)
    current = RobotPosition(100, 100, 180)
    t = Trajectory(speed=500)
    trajectory = t.get_trajectory(goal, current, current.distance_to(goal)/50)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    done = False
    while not done:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    done = True

        screen.fill(WHITE)

        for p in trajectory:
            pygame.draw.circle(screen, BLACK, p.astype(int), 3)

        pygame.display.flip()
