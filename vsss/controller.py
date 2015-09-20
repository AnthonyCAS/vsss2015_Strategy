from math.angles import normalize
from position import Position
from PID import PID
from move import MoveByVelocities


class Controller:
    """
    Hold the linear and angular PIDs for each robot,besides some util
    functions.
    """
    def __init__(self, lin_pid=PID(10, 10, 10), ang_pid=PID(0.2, 0.2, 0.2)):
        """
        :param lin_pid: Linear PID.
        :param ang_pid: Angular PID.
        :return: None.
        """
        self.lin_pid = lin_pid
        self.ang_pid = ang_pid

    def go_to_from(self, goal, start, speed=50, move_type='vel'):
        """
        Given a robot current position and a goal position, this function
        calculates the needed move to reach such goal.
        :param goal: The goal position.
        :param start: The current position of the robot
        :param speed: How fast the robot should get that position
        :param move_type; Which type of movement it should return. It can be
        'vel' for MoveByVelocities or 'pow' for MoveByPowers.
        :return: A subclass of MoveBase, either MoveByVelocities or
        MoveByPowers.
        """
        linerr, angerr = start.translation_error(goal)
        if abs(linerr) < 1:
            angerr = start.rotation_error(goal)
        linvel = max(-speed, min(speed, self.lin_pid.update(linerr)))
        angvel = min(8, max(-8, self.ang_pid.update(angerr)))

        if move_type == 'vel':
            return MoveByVelocities(linvel, angvel)
        elif move_type == 'pow':
            return MoveByVelocities(linvel, angvel).to_powers()
        else:
            raise ValueError("move_type can only be 'vel' or 'pow'")
