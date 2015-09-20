
class MoveBase(object):
    """
    This is a base class intended to be inherited by the classes implementing
    the distinct methods of movement of the robots.

    By the moment I write this we can have movement by linear velocities and
    movement by motor powers.
    """
    def is_quiet(self):
        """
        Determine if the movement will make the robot to stay in the same place
        """
        raise NotImplementedError()


class MoveByPowers(MoveBase):
    """
    This class is intended to hold the movement of the robots using left and
    right motor powers.
    """

    def __init__(self, left=99999, right=99999):
        """
        Initialize the object with the left and right motor powers. If you
        don't provide these parameters, the simulator will ignore this move.

        This works because the simulator ignores any attempt to move the
        robots with too high values like the default provided.
        :param left: Left motor power.
        :param right: Right motor power.
        :return: None.
        """
        self.left = left
        self.right = right

    def __str__(self):
        return '<MOVE> Left: %s, Right: %s' % (self.left, self.right)

    def is_quiet(self):
        return abs(self.left) < 5 and abs(self.right) < 5


class MoveByVelocities(MoveBase):
    """
    This class is intended to hold the movement of the robots using linear
    and angular velocities.
    """
    def __init__(self, linvel=99999, angvel=99999):
        """
        Initialize the object with the linear and angular velocities. If you
        don't provide these parameters, the simulator will ignore this move.

        This works because the simulator ignores any attempt to move the
        robots with too high values like the default provided.
        :param linvel: Linear velocity.
        :param angvel: Angular velocity.
        :return: None.
        """
        self.linvel = linvel
        self.angvel = angvel

    def __str__(self):
        return '<MOVE> Lin: %s, Ang: %s' % (self.linvel, self.angvel)

    def is_quiet(self):
        return abs(self.linvel) < 10 and abs(self.angvel) < 5

    def to_powers(self):
        return MoveByPowers(self.linvel + self.angvel, self.linvel - self.angvel)
