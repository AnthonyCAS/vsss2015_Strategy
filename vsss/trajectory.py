import numpy as np


class TrajectoryBase(object):
    def get_trajectory(self, goal, current, points_distance=10):
        """
        Return a set of intermediate points
        :param goal: RobotPosition where we want to go
        :param current: RobotPosition where we are now
        :return: List of intermediate points
        """
        raise NotImplementedError()


class TrajectoryHermit(TrajectoryBase):
    def __init__(self, speed_factor=5):
        self.speed_factor = speed_factor
        self.prev_point = None
        self.prev_vel = None

    def hermite(self, t, P=np.array([0, 4]), Q=np.array([2,5]), V=np.array([0, 500]), W=np.array([500, 0])):
        return P*(1-t)**2 * (2*t+1) + Q*t*t*(-2*t+3) + V*t*(t-1)**2 + W*(t-1)*t*t

    def hermite_vel(self, t, P=np.array([0, 4]), Q=np.array([2,5]), V=np.array([0, 500]), W=np.array([500, 0])):
        return P*6*t*(t-1) - Q*6*t*(t-1) + V*(3*t**2 - 4*t + 1) + W*t*(3*t - 2)

    def get_trajectory(self, goal, current, points_distance):
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
            V = current.theta_to_speed(dist*self.speed_factor)
            W = goal.theta_to_speed(dist*self.speed_factor)
        else:
            P = self.prev_point
            V = self.prev_vel
            W = self.prev_final_vel
            ret.append(current.to_numpy())

        Q = goal.to_numpy()

        intermediate_points = current.distance_to(goal)/points_distance
        step = 1.0/(intermediate_points+1)
        # print 'int', intermediate_points
        prev_gotten = False
        for t in np.arange(0, 1, step):
            p = self.hermite(t, P=P, Q=Q, V=V, W=W)
            ret.append(p)
            if not prev_gotten and np.linalg.norm(p-current.to_numpy()) > 10:
                prev_gotten = True
                self.prev_point = p
                self.prev_vel = (1-t)*self.hermite_vel(t, P=P, Q=Q, V=V, W=W)
                self.prev_final_vel = (1-t)*W
        if not prev_gotten:
            self.prev_point = None
            self.prev_vel = None
        ret.append(goal.to_numpy())
        return ret


class TrajectorySCurve(TrajectoryBase):
    def get_trajectory(self, goal, current, points_distance=10):
        pass









def hermit_test():
    import pygame
    from colors import *
    from position import RobotPosition

    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    goal = RobotPosition(700,500,0)
    current = RobotPosition(100, 100, 180)

    t = TrajectoryHermit(1)
    trajectory = t.get_trajectory(goal, current, 10)

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


def scurve_test():
    pass


if __name__ == "__main__":
    hermit_test()
