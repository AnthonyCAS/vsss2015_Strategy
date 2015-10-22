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
    return np.degrees(np.arccos(x))

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
    return (B-A)*(2*np.pi*r/360.0)

def vector_to(a, b):
    return b-a

def translate(a, v):
    return a+v

def angle_to(a, b):
    v = vector_to(a, b)
    return arctan2(v[1], v[0])

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
    return abs(angle-angle_to(point, right)) < abs(angle-angle_to(point, wrong))
