
class Move(object):
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

    @classmethod
    def combine(cls, a, b, v, w):
        """
        Combine two movements into one
        :param a: First movement
        :param b: Second movement
        :param v: First weight
        :param w: Second weight
        :return:
        """
        linvel = float(a.linvel * v + b.linvel.w)/(v+w)
        angvel = float(a.angvel * v + b.angvel.w)/(v+w)
        return Move(linvel, angvel)