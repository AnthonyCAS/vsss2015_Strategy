import time
import socket
import pygame

from colors import *


class TeamStrategyBase(object):
    """
    Wrap the strategy of a team. This class is intended to be inherited by your
    own strategy. You can override the method strategy(data) and call run()
    to start running your strategy.

    It basically handles the latency time and the communication through sockets.
    You have to be very careful with the latency time and choose one that lets
    your robots move fluently but without overloading the CONTROL_SERVER.

    If you set the latency to 0, your strategy will run with the latency the
    vision system uses to send messages. That's the faster your strategy can
    run.
    """

    latency = 50                # milliseconds
    serializer_class = None     # e.g. VsssSerializerSimulator
    use_vision = True
    do_visualize = False
    field_size = [150, 130]
    field_zoom = 3

    VISION_SERVER = None        # (ip, port) e.g. ('127.0.0.1', 9009)
    CONTROL_SERVER = None       # (ip, port) e.g. ('127.0.0.1', 9009)
    THIS_SERVER = None          # (ip, port) e.g. ('127.0.0.1', 9009)


    def __init__(self, team, team_size=3):
        """
        :param team: The team you're applying the strategy. You can import
        import either RED_TEAM or BLUE_TEAM from the settings.
        :param team_size: How many robots are there in your team?
        :return: None.
        """

        # Make sure you defined this class attributes in your child class
        if self.use_vision and self.VISION_SERVER is None:
            raise AttributeError('VISION_SERVER is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')
        if self.CONTROL_SERVER is None:
            raise AttributeError('CONTROL_SERVER is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')
        if self.THIS_SERVER is None:
            raise AttributeError('THIS_SERVER is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')
        if self.serializer_class is None:
            raise AttributeError('serializer is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')

        self.prev_time = time.time() * 1000         # milliseconds
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.THIS_SERVER)
        self.team = team
        self.team_size = team_size
        self.serializer = self.serializer_class(team, team_size)
        self.done = False

    def strategy(self, in_data):
        """
        Here you define the strategy at a high level.
        :param in_data: VsssInData object.
        :return: VsssOutData object.
        """
        raise NotImplementedError()

    def set_up(self):
        """
        This function is executed right at the beginning when you call run()
        and its purpose is to set_up some stuff.
        :return: None.
        """
        if self.do_visualize:
            pygame.init()
            self.screen_size = map(lambda x: x*self.field_zoom, self.field_size)
            self.screen = pygame.display.set_mode(self.screen_size)
            pygame.display.set_caption("Vsss strategy")

    def tear_down(self):
        """
        This function is executed right before run() finishes for whatever
        reason, even if you hit Ctrl-C.
        :return: None.
        """
        if self.do_visualize:
            pygame.quit()

    def run(self):
        """
        Handle the logic of the latency and socket communications. It calls
        set_up() at the beginning and tear_down() before finish.
        :return: None.
        """
        self.set_up()
        try:
            while not self.done:
                in_data = None
                if self.use_vision:
                    in_data, addr = self.sock.recvfrom(1024)
                cur_time = time.time() * 1000           # milliseconds
                if cur_time - self.prev_time > self.latency:
                    self.prev_time = cur_time
                    if self.use_vision:
                        in_data = self.serializer.load(in_data)
                    if self.do_visualize:
                        self.visualize(in_data)
                    out_data = self.strategy(in_data)
                    self.sock.sendto(self.serializer.dump(out_data),
                                     self.CONTROL_SERVER)
        finally:
            self.tear_down()

    def visualize(self, data):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.done = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.done = True
        colors = [RED, BLUE]
        self.screen.fill(WHITE)
        for i in range(self.team_size):
            team = data.teams[i]
            ball = data.ball

            for robot in team:
                pygame.draw.circle(
                    self.screen, colors[i], [int(robot.x * self.field_zoom),
                                        int(robot.y * self.field_zoom)],
                    5
                )
            pygame.draw.circle(self.screen, BLACK, [int(ball.x * self.field_zoom),
                                               int(ball.y * self.field_zoom)],
                               3)
        pygame.display.flip()


class TeamStrategySimulatorBase(TeamStrategyBase):
    """
    Add some functionality to make the strategy compatible with the simulator.
    You can inherit this class and use it exactly as TeamStrategyBase. The
    modifications are completely transparent to you.
    """
    def set_up(self):
        self.sock.sendto('', self.VISION_SERVER)
