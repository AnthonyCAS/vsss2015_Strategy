import numpy as np
from math.angles import normalize


class Position(object):
    """
    This class is intended to hold a position (x, y) without orientation, for
    example the position of the ball.

    The class which holds the robots' position will inherit from this class,
    and it will only add a new attribute to keep the orientation.

    For more info review documentation for __init__.
    """

    def __init__(self, x=0, y=0):
        """
        :param x: This axis is the longest side of the field.
        :param y: This axis is the shortest side of the field.
        :return: None.
        """
        self.x = x
        self.y = y

    def __str__(self):
        return 'x: %s, y: %s' % (self.x, self.y)

    def to_numpy(self):
        return np.array([self.x, self.y])

    def vector_to(self, target_pos):
        """
        Calculate a vector from this position to the target position.
        :param target_pos: The target position.
        :return: A 2 dimensional vector from this position to the
        target position.
        """
        return np.array([target_pos.x, target_pos.y]) - np.array(
            [self.x, self.y])

    def translate(self, vec):
        """
        Return a new Position object from this object translated by vec. It
        doesn't modify the actual position.
        :param vec: Translation vector desired.
        :return: New Position translated.
        """
        return Position(self.x + vec[0], self.y + vec[1])

    def distance_to(self, target_pos):
        """
        Calculate the euclidean distance from the current position to the target
        position.
        :param target_pos: The target position.
        :return: The distance from the current position to the target position.
        """
        v = self.vector_to(target_pos)
        return np.linalg.norm(v)

    def angle_to(self, target_pos, deg=True):
        """
        Calculate the angle from the current position to the target position.
        Without taking into account the orientation in any point.
        :type target_pos: Position.
        :param target_pos: The target position.
        :param deg: If true use degrees, else use radians.
        :return: Angle from the current position to the target position.
        """
        v = self.vector_to(target_pos)
        ang = np.arctan2(v[1], v[0])
        if deg:
            return normalize(ang * 180 / np.pi)
        else:
            return ang

    def move_origin(self, x, y):
        """
        Move the origin by (x, y). Return a new object without modifying this.
        """
        return Position(self.x - x, self.y - y)

    def clone(self):
        return Position(self.x, self.y)


class RobotPosition(Position):
    """
    Hold a position (x, y, theta) where theta is the orientation. This class
    is used to hold the robots' positions.
    """

    def __init__(self, x=0, y=0, theta=0):
        """
        :param theta: The orientation of the robot. In degrees.
        Angle zero points to the positive axis X and it increments counter
        clockwise.
        :return: None.
        """
        super(RobotPosition, self).__init__(x, y)
        self.theta = normalize(theta)

    def __str__(self):
        return 'x: %s, y: %s, theta: %s' % (self.x, self.y, self.theta)

    def __repr__(self):
        return self.__str__()


    def theta_to_speed(self, speed=100):
        return np.array([speed*np.cos(np.radians(self.theta)),
                         speed*np.sin(np.radians(self.theta))])

    def looking_to(self, dist=3):
        """
        :param dist: Distance from the center to the returned point.
        :return: A point in the direction where the robot is looking
        """
        return np.array([self.x, self.y]) + self.theta_to_speed(dist)

    def move_origin(self, x, y):
        """
        Move the origin by (x, y). Return a new object without modifying this.
        """
        return RobotPosition(self.x - x, self.y - y, self.theta)

    def translation_error(self, goal):
        """
        Calculate linear and angular distance errors to reach the goal position.
        :type goal: Position
        :param goal: The position where the robot wants to go.
        :return: Linear and angular errors to reach the goal position.
        """
        linerr = self.distance_to(goal)
        angerr1 = normalize(self.angle_to(goal) - self.theta)
        angerr2 = normalize(self.angle_to(goal) - (self.theta-180))
        if abs(angerr1) < abs(angerr2):
            return linerr, angerr1
        else:
            return -linerr, angerr2

    def rotation_error(self, goal):
        """
        This method should be called when the robot doesn't need to translate
        itself because it's already in the (x, y) of the goal position.

        If the robot needs to translate to a different (x, y) position, use
        translation_error.

        :param goal: The position including the orientation the robot wants.
        The current position (x, y) and the goal (x, y) must be very near.
        :return: Angular error to reach the goal orientation.
        """
        angerr1 = normalize(goal.theta - self.theta)
        angerr2 = normalize(goal.theta - (self.theta-180))
        if abs(angerr1) < abs(angerr2):
            return angerr1
        else:
            return angerr2

    def clone(self):
        return RobotPosition(self.x, self.y, self.theta)