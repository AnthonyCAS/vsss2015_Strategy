import sys
import pygame
from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
from vsss.trajectory import Trajectory
from vsss.visualizer import VsssVisualizer
from vsss.colors import *

trajectory = None

class TrajectoryVisualizer(VsssVisualizer):
    def extra_visualize(self):
        if trajectory is not None:
            global trajectory
            trajectory = [self.to_screen(x).tonp() for x in trajectory]
            pygame.draw.lines(self.screen, GREEN, False, trajectory, 1)
            for p in trajectory:
                pygame.draw.circle(self.screen, GREEN, p, 3, 3)
            pygame.draw.circle(self.screen, BLUE, trajectory[1], 3, 3)

            

class BalonAlArcoStrategy(TeamStrategyBase):
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 9001)
    serializer_class = VsssSerializerSimulator
    do_visualize = True
    visualizer_class = TrajectoryVisualizer

    def set_up(self):
        super(BalonAlArcoStrategy, self).set_up()
        self.controller = Controller()
        self.traj = Trajectory()

    def strategy(self, data):
        global trajectory
        team = data.teams[self.team]
        ball = data.ball
        goal = RobotPosition(ball.x, ball.y, ball.angle_to(Position(75, 0)))
        current = team[0]

        trajectory = self.traj.get_trajectory(goal, current,
                                         current.distance_to(goal)/10.0)
        intermediate = Position.fromnp(trajectory[1])
        # print current, intermediate
        move = self.controller.go_to_from(intermediate, current)

        out_data = VsssOutData()
        out_data.moves.append(move)
        return out_data


if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./vision_test 0
        ./vision_test 1"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_color = int(sys.argv[1])
    strategy = BalonAlArcoStrategy(my_color, 1)
    strategy.run()
