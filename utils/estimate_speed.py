import pygame
from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase, FirstTimeStrategy
from vsss.visualizer import VsssVisualizer
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.move import Move
from vsss.position import RobotPosition, Position
from vsss.vsss_math.angles import normalize


class EstimateSpeedStrategy(FirstTimeStrategy):
    do_visualize = True
    use_vision = True
    latency = 0

    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerSimulator
    def set_up(self):
        super(EstimateSpeedStrategy, self).set_up()
        self.controller = Controller()
        self.one_points = []
        self.two_points = []
        self.three_points = []

    def strategy(self, data):
        team = data.teams[self.team]
        for i, (robot, goal) in enumerate(zip(team, self.goals)):
            if robot.distance_to(goal) < 2:
                self.goals[i].x = -goal.x


    def do_on_first_time(self, data):
        self.goals = []
        team = data.teams[self.team]
        moves = []
        for robot in team:
            if robot.y > 0:
                goal = RobotPosition(-60, robot.y, 180)
            else:
                goal = RobotPosition(60, robot.y, 0)
            self.goals.append(goal)
            moves.append(self.controller.go_to_from(goal, robot))

        out_data = VsssOutData(moves=moves)
        return out_data


if __name__ == '__main__':
    my_color = 0
    strategy = EstimateSpeedStrategy(my_color, 3)
    
    strategy.run()
