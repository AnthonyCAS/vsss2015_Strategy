import numpy as np

RED_TEAM = 0
BLUE_TEAM = 1


def normalize_angle(angle):
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


class Position:
    def __init__(self, x, y, theta=0):
        self.x = x
        self.y = y
        self.theta = normalize_angle(theta)

    def __str__(self):
        return 'x: %s, y: %s, theta: %s' % (self.x, self.y, self.theta)

    def vector_to(self, position):
        return np.array([position.x, position.y]) - np.array([self.x, self.y])

    def translate(self, vec):
        return Position(self.x + vec[0], self.y + vec[1])

    def distance_to(self, position):
        v = self.vector_to(position)
        return np.linalg.norm(v)

    def angle_to(self, position, deg=True):
        v = self.vector_to(position)
        ang = np.arctan2(v[1], v[0])
        if deg:
            return normalize_angle(ang*180/np.pi)
        else:
            return ang

class Move:
    def __init__(self, linvel=99999, angvel=99999):
        self.linvel = linvel
        self.angvel = angvel

    def __str__(self):
        return '<MOVE> Lin: %s, Ang: %s' % (self.linvel, self.angvel)

    def is_quiet(self):
        return abs(self.linvel) < 10 and abs(self.angvel) < 5