import numpy as np
from vsss_math.angles import *
from vsss_math.arithmetic import *
from colors import *

class TrajectoryBase(object):
    def clean_trajectory(self, traj, points_distance):
        new_traj = [traj[0]]
        for i in xrange(len(traj)-1):
            if distance(traj[i], traj[i+1]) >= points_distance:
                new_traj.append(traj[i+1])
        if len(new_traj) < 2:
            new_traj = [traj[0], traj[-1]]
        return new_traj

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
        return self.clean_trajectory(ret, points_distance)


class TrajectorySCurve(TrajectoryBase):
    distance_to_border = 10
    def __init__(self, r=30):
        self.r = r

    # def point_near_border(self, point):
    #     return point[0] < -75 + self.
    #
    # def check_borders(self, traj):
    #     pass

    def get_trajectory(self, goal, current, points_distance=10):
        # A, B, C, D -> angles
        A = current.theta
        B = goal.theta

        # a,b,c,d -> points
        a = current.tonp()
        b = goal.tonp()
        currentDistance = distance(a, b)
        # angular step for desired points_distance
        ang_step = points_distance*360.0/(2*np.pi*self.r)

        # Vars to calculate best trajectory
        minlen = 99999
        ret = []
        if currentDistance >  4*self.r:
            # sentidos horario=-1 antihorario=+1
            # sa: sentido de a; sb: sentido de b
            for sa in [-1, 1]:
                for sb in [-1, 1]:
                    # Get the circle in the current sa
                    a1 = move_by_radius(a, self.r, A+90*sa)

                    # Get the circle in the current sb
                    b1 = move_by_radius(b, self.r, B+90*sb)

                    C = angle_to(a1, b1)

                    if sa == sb: # parallel
                        # tangent 1, point 1
                        t1p1 = move_by_radius(a1, self.r, C-90)
                        # tangent 2, point 1
                        t2p1 = move_by_radius(a1, self.r, C+90)

                        # Decide which tangent is the correct one
                        if circle_right_direction(a1, self.r, sa, t1p1, C):
                            # tangent angle
                            tA = -90
                            # tangent point 1
                            tp1 = t1p1
                        else:
                            tA = 90
                            tp1 = t2p1
                        # tangent point 2
                        tp2 = move_by_radius(b1, self.r, C+tA)
                    else: # cross
                        dist = distance(a, b)
                        D = arccos(2.0*self.r/dist)
                        t1p1 = move_by_radius(a1, self.r, C+D)
                        t2p1 = move_by_radius(a1, self.r, C-D)

                        if circle_right_direction(a1, self.r, sa, t1p1, C+D-90):
                            tA = -D
                            tp1 = t1p1
                        else:
                            tA = D
                            tp1 = t2p1
                        tp2 = move_by_radius(b1, self.r, C+tA)


                    # Points of arc1
                    D = A-90*sa
                    if sa == sb:
                        E = C+tA
                    else:
                        E = C-tA

                    # Points of arc2
                    F = B-90*sb
                    G = C+tA

                    # Length of arcs
                    arc1 = arclen(D, E, self.r)
                    arc2 = arclen(G, F, self.r)

                    # Length of tangent
                    tlen = distance(tp1, tp2)

                    # Length of path
                    pathlen = arc1 + arc2 + tlen

                    # Update path if it's the shortest one
                    if pathlen < minlen:
                        minlen = pathlen
                        ret = []
                        for i in angle_range(D, E, sa*ang_step):
                            ret.append(move_by_radius(a1, self.r, i))
                        ret.append(tp1)

                        for i in angle_range(G, F, sb*ang_step):
                            ret.append(move_by_radius(b1, self.r, i))
                        ret.append(b)
        else:
            # where a is the first point and b third point of the curve
    
            for sb in [-1, 1]:
                print 'Second way'
                # Get the circle in the current sb
                center = move_by_radius(b, self.r, B+90*sb)
                hipho =  distance(a, center)
                alpha =  arcsin (self.r/hipho)
                beta = 90-alpha
                R =  angle_to(center,a)
                t1p2 = move_by_radius(center, self.r, R-beta)
                t2p2 = move_by_radius(center, self.r, normalize(R+beta))

                if circle_right_direction(center, self.r, sb, t1p2, angle_to(a, t1p2)):
                    tp2 = t1p2
                    G = R-beta
                else:
                    tp2 = t2p2
                    G = R+beta

                lin = distance (a, tp2)
                  
                F = angle_to(center, b)
                arc1 = arclen(G, F, self.r)
                length_path = lin + arc1

                if length_path < minlen:
                    # Length of arcs
                    ret = []
                    ret.append(a)
                    ret.append(tp2)

                    
                    minlen = length_path
                    for i in angle_range(G, F, sb*ang_step):
                        ret.append(move_by_radius(center, self.r, i))
                    ret.append(b)

        return self.clean_trajectory(ret, points_distance)


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

    current = RobotPosition(500, 500, 45)
    goal = RobotPosition(520,520,-45)

    t = TrajectorySCurve()
    trajectory = t.get_trajectory(goal, current, 1)
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
        GREEN = (0, 255, 0)
        pygame.draw.circle(screen, GREEN, (current.x, 600 - current.y),2)
        pygame.draw.circle(screen, GREEN, (goal.x, 600 - goal.y),2)
        for i in xrange(len(trajectory)-1):
            pygame.draw.line(screen, BLACK, trajectory[i], trajectory[i+1], 3)

        pygame.display.flip()


if __name__ == "__main__":
    scurve_test()
