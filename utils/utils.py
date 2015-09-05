from .PID import PID
from .core import Move, normalize_angle



def robot_error_translation(goal, start):
    linerr = start.distance_to(goal)
    angerr1 = normalize_angle(start.angle_to(goal) - start.theta)
    angerr2 = normalize_angle(start.angle_to(goal) - (start.theta-180))
    if abs(angerr1) < abs(angerr2):
        return linerr, angerr1
    else:
        return -linerr, angerr2

def robot_error_rotation(goal, start):
    angerr1 = normalize_angle(goal.theta - start.theta)
    angerr2 = normalize_angle(goal.theta - (start.theta-180))
    if abs(angerr1) < abs(angerr2):
        return angerr1
    else:
        return angerr2


def go_to_from(goal, start, speed=50):
    linerr, angerr = robot_error_translation(goal, start)
    if abs(linerr) < 1:
        angerr = robot_error_rotation(goal, start)
    linvel = max(-speed, min(speed, go_to_from.lin_pid.update(linerr)))
    angvel = min(8, max(-8, go_to_from.ang_pid.update(angerr)))
    return Move(linvel, angvel)

go_to_from.lin_pid = PID(10, 10, 0)
go_to_from.ang_pid = PID(0.2, 0.2, 0)