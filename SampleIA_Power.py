#!/usr/bin/python

import sys

from vsss.strategy import TeamStrategySimulatorBase
from vsss.settings import *

from vsss.serializer import VsssSerializerSimulator
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
from vsss.data import VsssOutData
from vsss.move import MoveByVelocities
from vsss.math.angles import normalize


def ball_to_center(player, ball, goal, controller):
    print('Ball to center')
    if player.distance_to(ball) < 5:
        if player.angle_to(goal) > 0:
            return (0, 20)
        else:
            return MoveByVelocities(0, -20).to_powers()
    else:
        return controller.go_to_from(ball, player)


def go_to_shooting_pos(player, ball, goal, controller):
    print('go to shooting pos')
    if not abs(player.angle_to(goal) - ball.angle_to(goal)) < 0.2:
        vec_ball_to_del = goal.vector_to(ball) / goal.distance_to(ball)
        dest = ball.translate(vec_ball_to_del * 5)
        dest.theta = normalize(ball.angle_to(goal))
    else:
        dest = Position(player.x, player.y)
        dest.theta = player.angle_to(goal)
    return controller.go_to_from(dest, player)


def shoot(player, ball, goal, controller):
    print('shoot')
    move = controller.go_to_from(goal, player, speed=75)
    return move


def idle(player, ball, goal, controller):
    print('idle')
    return controller.go_to_from(controller.initial, player)


class PlayerState:
    def __init__(self, state):
        self.state = state

    def get_move(self, player, ball, goal, controller):
        return self.state(player, ball, goal, controller)


def get_portero_move(my_color, player, ball, goal, controller):
    dest = RobotPosition(ball.x, ball.y)
    dest.theta = 90

    dest.y = min(16.5, max(-16.5, dest.y))
    if my_color == RED_TEAM:
        dest.x = 68
    else:
        dest.x = -68
    return controller.go_to_from(dest, player)


delantero_state = PlayerState(go_to_shooting_pos)


def get_delantero_move(my_color, player, ball, goal, controller):
    if abs(goal.x - ball.x) < 80:
        if abs(ball.y) > 60 or abs(ball.x) > 70:
            delantero_state.state = ball_to_center
        elif (abs(player.angle_to(goal) - ball.angle_to(goal)) < 1 and
                      player.distance_to(goal) > ball.distance_to(goal)):
            delantero_state.state = shoot
        else:
            delantero_state.state = go_to_shooting_pos
    else:
        delantero_state.state = idle

    move = delantero_state.get_move(player, ball, goal, controller)
    return move


medio_state = PlayerState(go_to_shooting_pos)


def get_medio_move(my_color, player, ball, goal, controller):
    if abs(goal.x - ball.x) > 80:
        if abs(ball.y) > 60 or abs(ball.x) > 70:
            medio_state.state = ball_to_center
        elif (abs(player.angle_to(goal) - ball.angle_to(goal)) < 1 and
                      player.distance_to(goal) > ball.distance_to(goal)):
            medio_state.state = shoot
        else:
            medio_state.state = go_to_shooting_pos
    else:
        medio_state.state = idle

    move = medio_state.get_move(player, ball, goal, controller)
    return move


class Test_strategy(TeamStrategySimulatorBase):
    serializer_class = VsssSerializerSimulator
    VISION_SERVER = ('', 9009)
    CONTROL_SERVER = ('', 9009)
    THIS_SERVER = ('', 9010)

    def set_up(self):
        """
        Function to set robots position up and initialize the communication with
        vision server
        """
        self.opposite_goal = Position(-75, 0)
        self.my_goal = Position(75, 0)
        if self.team == BLUE_TEAM:
            self.opposite_goal, self.my_goal = self.my_goal, self.opposite_goal

        super(Test_strategy, self).set_up()
        self.goalkeeper_controller = Controller(initial=self.my_goal)
        if self.team == RED_TEAM:
            self.forward_controller = Controller(initial=RobotPosition(0, 0, 180),
                                                 move_type='pow')
            self.defence_controller = Controller(initial=RobotPosition(50, 10, 180),
                                                 move_type='pow')
        else:
            self.forward_controller = Controller(initial=RobotPosition(0, 0, 0),
                                                 move_type='pow')
            self.defence_controller = Controller(initial=RobotPosition(-50, -10, 0),
                                                 move_type='pow')

    def strategy(self, data):

        my_team = data.teams[self.team]
        ball = data.ball

        out_data = VsssOutData()

        out_data.moves.append(
            get_portero_move(self.team, my_team[0], ball, self.opposite_goal,
                             self.goalkeeper_controller))

        out_data.moves.append(
            get_medio_move(self.team, my_team[1], ball, self.opposite_goal,
                           self.defence_controller))

        out_data.moves.append(
            get_delantero_move(self.team, my_team[2], ball, self.opposite_goal,
                               self.forward_controller))

        return out_data


if __name__ == '__main__':
    def help():
        return 'Usage:\n    %s\n    %s' % ('For red team: ./SampleIA_Power 0',
                                           'For blue team:./SampleIA_Power 1')


    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    team = int(sys.argv[1])
    hardplay = Test_strategy(team, 3)
    hardplay.run()
