import sys
import pygame
from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
from vsss.trajectory import TrajectorySCurve
from vsss.visualizer import VsssVisualizer
from vsss.move import Move
from vsss.colors import *
from vsss.vsss_math.arithmetic import *

trajectory = None
my_side = 0

class TrajectoryVisualizer(VsssVisualizer):
    def extra_visualize(self):
        global trajectory
        if trajectory is not None:
            trajectory = [self.to_screen(x).tonp() for x in trajectory]
            pygame.draw.lines(self.screen, GREEN, False, trajectory, 1)
            for p in trajectory:
                pygame.draw.circle(self.screen, GREEN, p, 3, 3)
            pygame.draw.circle(self.screen, BLUE, trajectory[1], 3, 3)

            

class BalonAlArcoStrategy(TeamStrategyBase):
    CONTROL_SERVER = ('0.0.0.0', 9003)
    serializer_class = VsssSerializerSimulator
    do_visualize = True
    latency = 100
    print_iteration_time = False
    visualizer_class = TrajectoryVisualizer

    def set_up(self):
        super(BalonAlArcoStrategy, self).set_up()
        self.controller = Controller()
        self.traj = TrajectorySCurve(r=10)

    def strategy(self, data):
        global trajectory
        print "TEAM", data.teams
        team = data.teams[self.team]
        ball = data.ball
        if my_side == 0:
            goal = Position(-80,0)
        else:
            goal = Position(80,0)
        Abg = ball.angle_to(goal)   # angulo ball to goal
        obj = RobotPosition(ball.x, ball.y, Abg)
        current = team[1]

        if current.distance_to(ball) <= 8:
            new_obj = move_by_radius(ball.tonp(), 10, Abg)
            obj = RobotPosition(new_obj[0], new_obj[1], Abg)
        move = self.controller.go_with_trajectory(obj, current)
        trajectory = self.traj.get_trajectory(obj, current, 10)

        out_data = VsssOutData(moves=[
            Move(0,0),
            move,
            Move(0,0),
        ])
        return out_data


if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./vision_test 0 <puerto>
        ./vision_test 1 <puerto>"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 3:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_side = int(sys.argv[1])
    strategy = BalonAlArcoStrategy(my_side, 3, this_server=("0.0.0.0", int(sys.argv[2])))
    strategy.run()
