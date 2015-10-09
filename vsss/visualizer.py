import pygame

from colors import *
from position import Position


class VsssVisualizer(object):
    field_size = [150, 130]

    def __init__(self, field_zoom=3):
        self.done = False
        self.field_zoom = field_zoom
        self.screen_size = map(lambda x: x*self.field_zoom, self.field_size)
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Vsss strategy")
        pygame.init()


    def to_screen(self, pos):
        """
        Does not modify original pos. Converto from field space to screen space.
        :param pos: Position or RobotPosition
        :return: new Position ready to draw on screen
        """
        if pos.__class__.__name__ == "ndarray":
            pos = Position.from_numpy_array(pos)
        pos = pos.clone()
        pos.y = -pos.y
        if hasattr(pos, 'theta'):
            pos.theta = -pos.theta
        pos = pos.move_origin(-75, -65)
        pos.x = int(pos.x*self.field_zoom)
        pos.y = int(pos.y*self.field_zoom)
        return pos


    def visualize(self, data, extra_visualization=None):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.done = True
        colors = [RED, BLUE]
        self.screen.fill(WHITE)
        for i in range(2):
            team = data.teams[i]

            for robot in team:
                robot = self.to_screen(robot)
                center = [robot.x, robot.y]
                pygame.draw.circle(self.screen, colors[i], center, 5)
                front = robot.looking_to(10)
                pygame.draw.line(self.screen, colors[i], center, front, 3)

            ball = self.to_screen(data.ball)
            center = [ball.x, ball.y]
            pygame.draw.circle(self.screen, BLACK, center, 3)
        self.extra_visualize()
        pygame.display.flip()
        return self.done

    def extra_visualize(self):
        """
        This is to be overriden
        """
        pass