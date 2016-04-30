import pygame
from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.visualizer import VsssVisualizer
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.move import Move
from vsss.position import RobotPosition, Position
from vsss.vsss_math.angles import normalize


click_pos = None

class ClickVisualizer(VsssVisualizer):
    def listen_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.done = True
            elif e.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()


vitoko_gay = True

class VisionTestStrategy(TeamStrategyBase):
    do_visualize = True
    use_vision = True
    latency = 0
    visualizer_class = ClickVisualizer

    THIS_SERVER = ('0.0.0.0', 9002)
    VISION_SERVER = ('127.0.0.1', 9001)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerReal
    def set_up(self):
        super(VisionTestStrategy, self).set_up()
        self.controller = Controller()

    def strategy(self, data):
        # global vitoko_gay
        # vitoko_gay = not vitoko_gay
        # if vitoko_gay:
        #     return VsssOutData(moves=[Move()]*3)
        # print data.teams, data.ball
        team = data.teams[self.team]
        ball = data.ball
        goal = RobotPosition(ball.x, ball.y, ball.angle_to(Position(75, 0)))

        out_data = VsssOutData(moves=[
            self.controller.go_to_from(goal, team[0]),
            Move(0,0),
            Move(0,0),
            # self.controller.go_to_from(goal, team[1]),
            # self.controller.go_to_from(goal, team[2]),
        ])
        print out_data.moves
        return out_data

if __name__ == '__main__':
    my_color = 0
    strategy = VisionTestStrategy(my_color, 3)
    
    strategy.run()
