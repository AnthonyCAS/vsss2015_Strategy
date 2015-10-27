

''' States for players '''


from vsss.controller import Controller
from vsss.position import RobotPosition, Position

from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase

'''
    functions to move the robots
'''
class stateMachine:
    def __init__(self):
        self.state = None

    def do_move(self, player, ball, objetive, controller):
        return self.state(player, ball, objetive, controller)

DefensorState = stateMachine()
#forwardState = stateMachine()

def shootingBall(currentPosition, ballPosition, objetive, controller):
    if currentPosition.distance_to(ballPosition) < 5:
        return controller.go_to_from(ballPosition, currentPosition)

def go_to_ball(currentPosition, ballPosition, objetive, controller):
    return controller.go_to_from(ballPosition, currentPosition)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

'''
Methods to manage the robot moves
'''
def get_defensor_move(color, currentPosition, ballPosition, objetive, controller):
    if abs(currentPosition.x - ballPosition.x) > 75:
        if abs(currentPosition.y - ballPosition.y) > 65:
            DefensorState.state = go_to_ball
        elif (abs(currentPosition.angle_to(objetive) - ballPosition.angle_to(objetive)) < 1 and
                      currentPosition.distance_to(objetive) > ballPosition.distance_to(objetive)):
            DefensorState.state = shootingBall
        else:
            DefensorState.state = None # estado
            return Move(0.1, 0.1)
    else:
        return Move(0.1, 0.1)

    move = DefensorState.do_move(currentPosition, ballPosition, objetive, controller)
    return move


def get_goalKeeper_move(color, currentPosition, ballPosition, objetive, controller):
    newPosition = RobotPosition(ballPosition.x, ballPosition.y)
    newPosition.theta = 90

    newPosition.y = min(16.5, max(-16.5, newPosition.y))
    if color == RED_TEAM:
        newPosition.x = 68
    else:
        newPosition.x = -68
    return controller.go_to_from(newPosition, currentPosition)

