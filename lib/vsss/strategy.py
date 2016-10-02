import socket
import time
from optparse import OptionParser

from visualizer import VsssVisualizer

from move import Move
from data import VsssOutData


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

    latency = 0                 # latency to send data to control server. In milliseconds. Zero means ASAP
    serializer_class = None     # e.g. VsssSerializerSimulator
    use_vision = True           # use vision server, if False, strategy will receive data=None
    use_control = True          # use control server, if False, strategy won't send data to control server
    do_visualize = False        # show pygame window with robot positions
    visualizer_class = VsssVisualizer
    field_zoom = 3
    print_iteration_time = False


    def __init__(self):
        """
        :param team: The team you're applying the strategy. You can import
        import either RED_TEAM or BLUE_TEAM from the settings.
        :param team_size: How many robots are there in your team?
        :return: None.
        """

        parser = OptionParser()
        parser.add_option("-p", "--port", dest="port", default=9002,
                          help="Port of strategy server", metavar="FILE")
        parser.add_option("-c", "--control-port", dest="control_port", default=9003,
                          help="Port of control server")
        parser.add_option("-s", "--team-size", dest="team_size", default=3,
                          help="Number of team players: 1, 2 or 3")
        parser.add_option("-t", "--team", dest="team_color",
                          help="Team color: 'blue' or 'yellow'")
        (self.options, args) = parser.parse_args()

        self.THIS_SERVER = ('127.0.0.1', self.options.port)
        self.CONTROL_SERVER = ('127.0.0.1', self.options.control_port)
        print "RUNNING ON", self.THIS_SERVER
        print "SENDING CONTROL DATA TO", self.CONTROL_SERVER

        self.prev_time = time.time()         # milliseconds
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.THIS_SERVER)
        self.serializer = self.serializer_class()
        self.done = False
        

    def call_strategy(self, in_data):
        return self.strategy(in_data)

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
        if self.use_control:
            out_data = VsssOutData(moves=[Move(0,0)]*3)
            self.sock.sendto(self.serializer.dump(out_data), self.CONTROL_SERVER)


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

                start_time = time.time()
                if start_time - self.prev_time >= self.latency/1000.0:
                    if self.use_vision:
                        in_data = self.serializer.load(in_data)
                    if in_data:
                        out_data = self.call_strategy(in_data)
                        
                        if self.use_control and out_data is not None:                    
                            self.sock.sendto(self.serializer.dump(out_data),
                                             self.CONTROL_SERVER)
                        if self.do_visualize:
                            self.done = self.visualizer.visualize(in_data)

                    end_time = time.time()
                    if self.print_iteration_time:
                        it_time = end_time - start_time
                        print "Time between: ", self.start_time - self.prev_time, "\t", "Iteration: ", it_time

                    self.prev_time = start_time
        except Exception as e:
            print "EXCEPTION!", e
        finally:
            self.tear_down()
            print 'tear down'


class FirstTimeStrategy(TeamStrategyBase):
    def __init__(self, team, team_size):
        super(FirstTimeStrategy, self).__init__(team, team_size)
        self.first_time = True

    def call_strategy(self, in_data):
        if self.first_time:
            return self.do_on_first_time(in_data)
        else:
            return self.strategy(in_data)

    def do_on_first_time(self, data):
        raise NotImplementedError()
