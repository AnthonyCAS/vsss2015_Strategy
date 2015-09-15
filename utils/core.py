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
    """ Clase posición, contiene funciones para calcular la distancia hacia otra posición
        También podemos calcular el ángulo de orientación normalizado.
    """
    def __init__(self, x=0, y=0, theta=0):
        """ x and y:
                Coordenadas de la posición actual del objeto.
            theta:
                Es el ángulo de orientación del objeto (Robots y balón).
        """
        self.x = x
        self.y = y
        self.theta = normalize_angle(theta)
    #to print
    def __str__(self):
        return 'x: %s, y: %s, theta: %s' % (self.x, self.y, self.theta)

    def vector_to(self, position):
        return np.array([position.x, position.y]) - np.array([self.x, self.y])
    #trasladar el objeto
    def translate(self, vec):
        return Position(self.x + vec[0], self.y + vec[1])
    #distancia entre dos puntos usando euclides
    def distance_to(self, position):
        v = self.vector_to(position)
        return np.linalg.norm(v)
    #get angle, if deg flag is set true = grades
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
