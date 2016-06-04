from PID import PID
from move import Move
from position import Position, RobotPosition
from trajectory import TrajectorySCurve
from vsss_math.arithmetic import *
from vsss_math.angles import *

import numpy as np

class Controller:
    """
    Hold the linear and angular PIDs for each robot,besides some util
    functions.
    """
    def __init__(self, lin_pid=PID(0.05, 0, 0.01),
                 ang_pid=PID(0.03, 0, 0.05),
                 trajectory_generator=TrajectorySCurve(r=10)):
        """
        :param lin_pid: Linear PID.
        :param ang_pid: Angular PID.
        :param move_type; Which type of movement it should return. It can be
        'vel' for MoveByVelocities or 'pow' for MoveByPowers.
        :return: None.
        """
        self.lin_pid = lin_pid
        self.ang_pid = ang_pid
        self.trajectory_generator = trajectory_generator

    def get_reference_to_avoid_obstacle(self, current, goal, obstacle):
        d = current.distance_to(obstacle)
        if d < 15:
            e = 90.0
        else:
            e = np.degrees(np.arcsin(15.0/d))
        angle1 = min_angle_between(current.angle_to(obstacle)+e, current.angle_to(goal))
        angle2 = min_angle_between(current.angle_to(obstacle)-e, current.angle_to(goal))
        if angle1 < angle2:
            ref = current.translate_polar(d, current.angle_to(obstacle)+e)
        else:
            ref = current.translate_polar(d, current.angle_to(obstacle)-e)
        return ref

    def collision(self, current, goal, obstacles):
        projections = []
        for i in [7,10,20, 30]:
            projections.append(current.translate_polar(i, current.angle_to(goal)))
        for obstacle in obstacles:
            for projection in projections:
                if obstacle.distance_to(projection) < 15:
                    return obstacle
        return None

    def get_reference_position(self, goal, current, obstacles=[]):
        obstacle = self.collision(current, goal, obstacles)
        if obstacle is not None:
            return self.get_reference_to_avoid_obstacle(current, goal, obstacle)
        # if abs(current.angle_to(goal)-goal.theta)<10:
        #     return goal
        beta = current.angle_to(goal)
        gama = beta - goal.theta

        dist = current.distance_to(goal)
        # dist \in [0, 180] transforms to LIM \in [90, 0]
        LIM = 90 - dist/2
        # Cuando LIM=90 se abre mucho para llegar al angulo adecuado. Se abre
        # menos a medida que LIM se reduce, pero no siempre es conveniente
        if dist > 40:
            LIM = 30
        elif dist < 30:
            LIM = 60
        else:
            LIM = 60-3*(dist-30)
        gama = min(LIM, max(-LIM, gama)) # gama between [-90; 90]
        # LIM_INF = LIM
        # if gama > -LIM_INF and gama < LIM_INF:
        #     gama = 0
        
        linerr, angerr = current.translation_error(goal)
        return current.translate_polar(linerr, beta+gama)

    def go_to_from_with_angle(self, goal, current, vel=1, obstacles=[]):
        # ref1 = goal.translate_polar(10, goal.theta-180)
        ref = self.get_reference_position(goal, current, obstacles)
        # if current.distance_to(ref) < 15:
        #     ref = goal
        move = self.go_to_from(ref, current, vel)
        return move


    def go_to_from(self, goal, current, vel=1):
        """
        Given a robot current position and a goal position, this function
        calculates the needed move to reach such goal.
        :rtype : MoveBase.
        :param goal: The goal position.
        :param current: The current position of the robot.
        :param speed: How fast the robot should get that position.
        :return: Move
        """
        linerr, angerr = current.translation_error(goal)
        linvel = vel*max(-1, min(1, self.lin_pid.update(linerr)))
        angvel = min(1, max(-1, self.ang_pid.update(angerr)))

        return Move(linvel, angvel)

    def go_with_trajectory(self, goal, current, points_distance=10.0):
        """
        Create a trajectory to go to the desired goal
        :param goal: RobotPosition where we want to go
        :param current: RobotPosition where we are now
        :return: Move
        """
        path = self.trajectory_generator.get_trajectory(
            goal, current, points_distance)
        if path is None:
            alternative_angles = range(-180,180, 45)
            distances = [abs(normalize(goal.theta-angle)) for angle in alternative_angles]
            for dist, angle in sorted(zip(distances, alternative_angles)):
                path = self.trajectory_generator.get_trajectory(
                            RobotPosition(goal.x, goal.y, angle), current, points_distance)
                if path is not None:
                    break
        if path is None:
            return self.go_to_from(goal, current)
        intermediate = Position.fromnp(path[1])
        return self.go_to_from(intermediate, current)


    def go_to_from_with_ball(self, goal, current, ball):
        move_to_goal = self.go_to_from(goal, current)
        move_to_ball = self.go_to_from(ball, current)
        return Move.combine(move_to_goal, move_to_ball, 1, 1)

    def do_rotation(self, goal, current):
        linerr, angerr = current.rotation_error(goal)
        linvel = max(-1, min(1, self.lin_pid.update(linerr)))
        angvel = min(1, max(-1, self.ang_pid.update(angerr)))
        return  Move(linvel, angvel)


