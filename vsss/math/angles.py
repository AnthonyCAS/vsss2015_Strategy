def normalize(angle, lower=-180, upper=180):
    while angle >= upper:
        angle -= 360
    while angle < lower:
        angle += 360
    return angle
