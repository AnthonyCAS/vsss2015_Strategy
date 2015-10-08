import sys
import pygame
from math import pi

from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategySimulatorBase, TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move


# Define the colors we will use in RGB format
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (  0,   0, 255)
GREEN = (  0, 255,   0)
RED =   (255,   0,   0)

# Set the height and width of the screen
field_size = [150, 130]
enlargement = 3
screen_size = map(lambda x: x*enlargement, field_size)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Test vision")


class SimulatorVisionTestStrategy(TeamStrategySimulatorBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    VISION_SERVER = ('0.0.0.0', 9001)
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.1', 9003)

    serializer_class = VsssSerializerSimulator

    def strategy(self, data):
        colors = [RED, BLUE]
        screen.fill(WHITE)
        for i in range(2):
            team = data.teams[i]
            ball = data.ball

            for robot in team:
                robot.x += 75
                robot.y += 65
                pygame.draw.circle(
                    screen, colors[i], [int(robot.x * enlargement),
                                        int(robot.y * enlargement)],
                    5
                )
        pygame.display.flip()

        return VsssOutData(moves=[Move()]*3)


class VisionTestStrategy(TeamStrategyBase):
    VISION_SERVER = ('0.0.0.0', 9001)
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.136', 9003)

    serializer_class = VsssSerializerSimulator

    def strategy(self, data):
        colors = [RED, BLUE]
        screen.fill(WHITE)
        for i in range(2):
            team = data.teams[i]
            ball = data.ball

            print 'TEAM', str(ball)
            for robot in team:
                print 'robot', str(robot)
                pygame.draw.circle(
                    screen, colors[i], [int(robot.x * enlargement),
                                        int(robot.y * enlargement)],
                    5
                )
            pygame.draw.circle(screen, BLACK, [int(ball.x * enlargement),
                                               int(ball.y * enlargement)],
                               3)
        pygame.display.flip()

        return VsssOutData(moves=[Move()]*3)

if __name__ == '__main__':
    my_color = 0
    strategy = VisionTestStrategy(my_color, 3)

    pygame.init()
    strategy.run()
    pygame.quit()
