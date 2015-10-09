import socket
from utils import get_millis
from visualizer import VsssVisualizer


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
    use_vision = True           # use vision server, if False, strategy will receive data=None
    use_control = True          # use control server, if False, strategy won't send data to control server
    do_visualize = False        # show pygame window with robot positions
    visualizer_class = VsssVisualizer
    field_zoom = 3

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
        if self.use_control and self.CONTROL_SERVER is None:
            raise AttributeError('CONTROL_SERVER is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')
        if self.THIS_SERVER is None:
            raise AttributeError('THIS_SERVER is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')
        if self.serializer_class is None:
            raise AttributeError('serializer is not defined as a class '
                                 'attribute, see the docs for TeamStrategyBase')

        self.prev_time = get_millis()         # milliseconds
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
            self.visualizer = self.visualizer_class(field_zoom=self.field_zoom)

    def tear_down(self):
        """
        This function is executed right before run() finishes for whatever
        reason, even if you hit Ctrl-C.
        :return: None.
        """
        pass


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
                cur_time = get_millis()           # milliseconds
                if cur_time - self.prev_time > self.latency:
                    self.prev_time = cur_time
                    if self.use_vision:
                        in_data = self.serializer.load(in_data)
                    if self.do_visualize:
                        self.done = self.visualizer.visualize(in_data)
                    out_data = self.strategy(in_data)
                    if self.use_control:
                        self.sock.sendto(self.serializer.dump(out_data),
                                         self.CONTROL_SERVER)
        finally:
            self.tear_down()
