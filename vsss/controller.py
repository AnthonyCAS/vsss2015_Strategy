from math.angles import normalize
from position import Position
from PID import PID
from move import MoveByVelocities
from settings import MOVE_BY_POW, MOVE_BY_VEL
from exceptions import MoveTypeError


class Controller:
    """
    Hold the linear and angular PIDs for each robot,besides some util
    functions.
    """
    def __init__(self, initial, lin_pid=PID(10, 10, 10),
                 ang_pid=PID(0.2, 0.2, 0.2), move_type=MOVE_BY_VEL):
        """
        :param lin_pid: Linear PID.
        :param ang_pid: Angular PID.
        :param move_type; Which type of movement it should return. It can be
        'vel' for MoveByVelocities or 'pow' for MoveByPowers.
        :param initial: RobotPosition Where the robot should go back when it's
        idle.
        :return: None.
        """
        self.lin_pid = lin_pid
        self.ang_pid = ang_pid
        self.move_type = move_type
        self.initial = initial

    def go_to_from(self, goal, current, speed=50):
        """
        Given a robot current position and a goal position, this function
        calculates the needed move to reach such goal.
        :rtype : MoveBase.
        :param goal: The goal position.
        :param current: The current position of the robot.
        :param speed: How fast the robot should get that position.
        :return: A subclass of MoveBase, either MoveByVelocities or
        MoveByPowers.
        """
        linerr, angerr = current.translation_error(goal)
        if abs(linerr) < 1:
            angerr = current.rotation_error(goal)
        linvel = max(-speed, min(speed, self.lin_pid.update(linerr)))
        angvel = min(8, max(-8, self.ang_pid.update(angerr)))

        if self.move_type == MOVE_BY_VEL:
            return MoveByVelocities(linvel, angvel)
        elif self.move_type == MOVE_BY_POW:
            return MoveByVelocities(linvel, angvel).to_powers()
        else:
            raise MoveTypeError()

    def go_to_initial(self, current, speed=50):
        """
        Similar to self.go_to_from, but the goal position is the initial
        position.
        :param current: The current position of the robot.
        :param speed: How fast the robot should get to the initial position.
        :return: A subclass of MoveBse, either MoveByVelocities or
        MoveByPowers.
        """
        self.go_to_from(self.initial, current, speed)
