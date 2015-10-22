from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase


class VisionTestStrategy(TeamStrategyBase):
    use_control = False
    do_visualize = True
    use_vision = True

    THIS_SERVER = ('127.0.0.1', 9002)
    VISION_SERVER = ('127.0.0.1', 9001)
    CONTROL_SERVER = ('127.0.0.1', 9001)
   
    serializer_class = VsssSerializerSimulator
    def set_up(self):
		super(VisionTestStrategy, self).set_up()
		self.sock.sendto('', self.VISION_SERVER)

    def strategy(self, data):
        print data.teams


if __name__ == '__main__':
    my_color = 0
    strategy = VisionTestStrategy(my_color, 1)
    
    strategy.run()
