from PID import PID
from move import Move
from position import Position


class Controller:
    """
    Hold the linear and angular PIDs for each robot,besides some util
    functions.
    """
    def __init__(self, lin_pid=PID(0.03, 0, 0.01),
                 ang_pid=PID(0.01, 0, 0)):
        """
        :param lin_pid: Linear PID.
        :param ang_pid: Angular PID.
        :param move_type; Which type of movement it should return. It can be
        'vel' for MoveByVelocities or 'pow' for MoveByPowers.
        :return: None.
        """
        self.lin_pid = lin_pid
        self.ang_pid = ang_pid

    def go_to_from(self, goal, current):
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
        linvel = max(-1, min(1, self.lin_pid.update(linerr)))
        angvel = min(1, max(-1, self.ang_pid.update(angerr)))

        return Move(linvel, angvel)

    def go_with_trajectory(self, goal, current):
        """
        Create a trajectory to go to the desired goal
        :param goal: RobotPosition where we want to go
        :param current: RobotPosition where we are now
        :return: Move
        """
        traj = Trajectory()
        trajectory = traj.get_trajectory(goal, current,
                                         current.distance_to(goal)/10.0)
        intermediate = Position.fromnp(trajectory[1])
        print current, intermediate
        return self.go_to_from(intermediate, current)

    def go_to_from_with_ball(self, goal, current, ball):
        move_to_goal = self.go_to_from(goal, current)
        move_to_ball = self.go_to_from(ball, current)
        return Move.combine(move_to_goal, move_to_ball, 1, 1)
