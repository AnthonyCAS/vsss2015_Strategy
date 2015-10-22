import numpy as np
from vsss_math.angles import *
from vsss_math.arithmetic import *
from colors import *

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
            return [current.tonp(), goal.tonp()]
        ret = []
        if self.prev_point is None:
            P = current.tonp()
            V = current.theta_to_speed(dist*self.speed_factor)
            W = goal.theta_to_speed(dist*self.speed_factor)
        else:
            P = self.prev_point
            V = self.prev_vel
            W = self.prev_final_vel
            ret.append(current.tonp())

        Q = goal.tonp()

        intermediate_points = current.distance_to(goal)/points_distance
        step = 1.0/(intermediate_points+1)
        # print 'int', intermediate_points
        prev_gotten = False
        for t in np.arange(0, 1, step):
            p = self.hermite(t, P=P, Q=Q, V=V, W=W)
            ret.append(p)
            if not prev_gotten and np.linalg.norm(p-current.tonp()) > 10:
                prev_gotten = True
                self.prev_point = p
                self.prev_vel = (1-t)*self.hermite_vel(t, P=P, Q=Q, V=V, W=W)
                self.prev_final_vel = (1-t)*W
        if not prev_gotten:
            self.prev_point = None
            self.prev_vel = None
        ret.append(goal.tonp())
        return ret


class TrajectorySCurve(TrajectoryBase):
    def get_trajectory(self, goal, current, points_distance=10):
        # A, B, C, D -> angles
        A = current.theta
        B = goal.theta

        # a,b,c,d -> points
        a = current.tonp()
        b = goal.tonp()
        # sentidos horario=-1 antihorario=+1
        if False: # Parallel trajectories
            sa = -1
            sb = -1

            r = 30
            # 2 circles from a
            a1 = move_by_radius(a, r, A+90*sa)
            # a2 = move_by_radius(a, r, A-90)

            # 2 circles from b
            b1 = move_by_radius(b, r, B+90*sb)
            # b2 = move_by_radius(b, r, B-90)

            # Points of parallel tangents:
            C = angle_to(a1, b1)
            t1p1 = move_by_radius(a1, r, C-90)
            t2p1 = move_by_radius(a1, r, C+90)
            if circle_right_direction(a1, r, sa, t1p1, C):
                print 'Taking first trajectory'
                tA = -90
                tp1 = t1p1
                tp2 = move_by_radius(b1, r, C+tA)
            else:
                tA = 90
                tp1 = t2p1
                tp2 = move_by_radius(b1, r, C+tA)

            # Length of paths for t1
            D = A-90*sa
            E = C+tA
            arc1 = arclen(D, E, r)
            # arc2 = arclen(B+90, C-90, r)
            # tlen = distance(tp1, tp2)
            # pathlen = arc1 + arc2 + tlen

            # print "DISTANCE", pathlen
            ret = [tp1, tp2, a, a1, b1, b]
            for i in angle_range(D, E, sa):
                ret.append(move_by_radius(a1, r, i))

            F = B-90*sb
            G = C+tA
            print G, F, angle_range(G, F, sb)
            for i in angle_range(G, F, sb):
                ret.append(move_by_radius(b1, r, i))
            return ret
        else:
            sa = 1
            sb = -1

            r = 30
            # 2 circles from a
            a1 = move_by_radius(a, r, A+90*sa)
            # a2 = move_by_radius(a, r, A-90)

            # 2 circles from b
            b1 = move_by_radius(b, r, B+90*sb)
            # b2 = move_by_radius(b, r, B-90)

            # Points of parallel tangents:
            C = angle_to(a1, b1)
            dist = distance(a, b)
            D = arccos(2.0*r/dist)
            t1p1 = move_by_radius(a1, r, C+D)
            t2p1 = move_by_radius(a1, r, C-D)
            if circle_right_direction(a1, r, sa, t1p1, C+D-90):
                print 'Taking first trajectory'
                tA = -D
                tp1 = t1p1
                tp2 = move_by_radius(b1, r, C+tA)
            else:
                tA = D
                tp1 = t2p1
                tp2 = move_by_radius(b1, r, C+tA)

            # Length of paths for t1
            D = A-90*sa
            E = C-tA
            arc1 = arclen(D, E, r)
            # arc2 = arclen(B+90, C-90, r)
            # tlen = distance(tp1, tp2)
            # pathlen = arc1 + arc2 + tlen

            # print "DISTANCE", pathlen
            ret = [tp1, tp2, a, a1, b1, b]
            for i in angle_range(D, E, sa):
                ret.append(move_by_radius(a1, r, i))

            F = B-90*sb
            G = C+tA
            for i in angle_range(G, F, sb):
                ret.append(move_by_radius(b1, r, i))
            return ret











def hermit_test():
    import pygame
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
    import pygame
    from position import RobotPosition

    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    current = RobotPosition(100, 500, 180)
    goal = RobotPosition(700,100,180)

    t = TrajectorySCurve()
    trajectory = t.get_trajectory(goal, current, 10)
    for i, p in enumerate(trajectory):
        trajectory[i] = arr(p[0], 600-p[1])

    done = False
    while not done:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    done = True

        screen.fill(WHITE)

        pygame.draw.line(screen, BLACK, trajectory[0], trajectory[1], 3)
        for p in trajectory:
            pygame.draw.circle(screen, BLACK, p.astype(int), 3)

        pygame.display.flip()


if __name__ == "__main__":
    scurve_test()
