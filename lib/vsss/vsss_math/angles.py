def normalize(angle, lower=-180, upper=180):
    while angle >= upper:
        angle -= 360
    while angle < lower:
        angle += 360
    return angle

def angle_range(begin, end, step, lower=-180, upper=180):
    begin = normalize(begin, lower=-180, upper=180)
    end = normalize(end, lower=-180, upper=180)
    ret = []
    i = begin
    while abs(normalize(end - i, lower=-180, upper=180)) >= abs(step):
        ret.append(i)
        i = normalize(i+step, lower=-180, upper=180)
    return ret

def min_angle_between(angle1, angle2):
    angle1 = normalize(angle1, 0, 360)
    angle2 = normalize(angle2, 0, 360)
    diff = abs(angle1-angle2)
    if diff > 180:
        diff = 360 - diff
    return diff