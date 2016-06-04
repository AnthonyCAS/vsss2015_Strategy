from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.move import Move
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.position import RobotPosition, Position
from vsss.visualizer import VsssVisualizer
from vsss.colors import *
import pygame
import time

temp_goal = Position(10,0)
prev_time = time.time()
print "YOLO"

class MyVisualizer(VsssVisualizer):
    def extra_visualize(self):
        global temp_goal
        center = self.to_screen(temp_goal)
        pygame.draw.circle(self.screen, GREEN, [center.x, center.y], 5)

class GoWithAngleStrategy(TeamStrategyBase):
    use_control = True
    do_visualize = True
    visualizer_class = MyVisualizer
    use_vision = True
    latency = 20

    THIS_SERVER = ('0.0.0.0', 9010)
    VISION_SERVER = ('0.0.0.0', 9009)
    CONTROL_SERVER = ('0.0.0.0', 9009)
   
    serializer_class = VsssSerializerSimulator
    def set_up(self):
        super(GoWithAngleStrategy, self).set_up()
        self.controller = Controller()
        self.file = open("data.txt", "w")

    def strategy(self, data):
        global temp_goal
        global prev_time
        cur_time = time.time()
        print "TIME ELAPSED:",time.time() - prev_time
        prev_time = cur_time
        goal = RobotPosition(data.ball.x, data.ball.y, data.ball.angle_to(Position(75, 0)))
        obstacles = data.teams[0]
        obstacles.extend(data.teams[1])
        obstacles.remove(data.teams[self.team][1])
        temp_goal = self.controller.get_reference_position(goal, data.teams[self.team][1], obstacles=obstacles)
        my_move = self.controller.go_to_from_with_angle(goal, data.teams[self.team][1], vel=1, obstacles=obstacles)
        self.file.write(str(data.teams[self.team][1])+"\n")
        if data.teams[self.team][1].distance_to(goal)<=9:
            my_move = Move(0,0)
        # if data.teams[self.team][1].has_in_front(goal):
            # my_move = self.controller.go_to_from(Position(75, 0), data.teams[self.team][1], vel=0.5)
        
        # my_move = self.controller.go_to_from(goal, data.teams[self.team][1], vel=0.5)

        return VsssOutData(moves=[
            Move(0,0),
            my_move,
            Move(0,0)
        ])

    def tear_down(self):
        super(GoWithAngleStrategy, self).tear_down()
        self.file.close()

print __name__
if __name__ == '__main__':
    my_color = 1
    strategy = GoWithAngleStrategy(my_color, 3)
    
    strategy.run()
