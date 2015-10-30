"""
All of the points and vectors used here are numpy arrays
First letters of the alphabet "a,b,c,d" are points
First block mayus letters "A, B, C, D" are angles
Least letters "v, w, x, y, z" are vectors
"""

import numpy as np
from angles import normalize

def arr(*args):
    return np.array(args)

def sin(A):
    return np.sin(np.radians(A))

def arcsin(x):
    return np.degrees(np.arcsin(x))

def arccos(x):
    return normalize(np.degrees(np.arccos(x)))

def cos(A):
    return np.cos(np.radians(A))

def arctan2(co, ca):
    """
    :param co: Number, cateto opuesto
    :param ca: Number, cateto adyacente
    :return: Degrees
    """
    ang = np.arctan2(co, ca)
    return normalize(np.degrees(ang))

def arclen(A, B, r):
    return normalize(B-A, 0, 360)*(2*np.pi*r/360.0)

def arclen_ori(A, B, r, ori):
    if ori > 0:
        ret = normalize(B-A, 0, 360)*(2*np.pi*r/360.0)
    elif ori < 0:
        ret = normalize(B-A, -360, 0)*(2*np.pi*r/360.0)
    else:
        raise Exception("ori must be -1 or 1")
    return abs(ret)

def vector_to(a, b):
    return b-a

def translate(a, v):
    return a+v

def angle_to(a, b):
    v = vector_to(a, b)
    return normalize(arctan2(v[1], v[0]))

def norm(v):
    return np.linalg.norm(v)

def distance(a, b):
    return norm(vector_to(a, b))

def move_by_radius(a, r, A):
    return a + arr(r*cos(A), r*sin(A))

def circle_right_direction(center, radius, sense, point, angle):
    """
    :param center: Circle center, np array
    :param sense: Clockwise=-1, Counterclockwise=1
    :param point: Point in circunference, np array
    :param angle: Degrees, direction starting from 'point'
    :return: Bool
    """
    A = angle_to(center, point)
    right = move_by_radius(center, radius, A+sense)
    wrong = move_by_radius(center, radius, A-sense)
    right_dist = abs(normalize(angle-angle_to(point, right), 0, 360))
    wrong_dist = abs(normalize(angle-angle_to(point, wrong), 0, 360))
    return right_dist < wrong_dist
