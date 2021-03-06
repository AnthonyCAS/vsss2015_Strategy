from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase


class VisionTestStrategy(TeamStrategyBase):
    use_control = False
    do_visualize = True
    use_vision = True

    THIS_SERVER = ('0.0.0.0', 9010)
    VISION_SERVER = ('127.0.0.1', 9009)
   
    serializer_class = VsssSerializerSimulator
    def set_up(self):
		super(VisionTestStrategy, self).set_up()

    def strategy(self, data):
        print data.teams, data.ball


if __name__ == '__main__':
    my_color = 0
    strategy = VisionTestStrategy(my_color, 2)
    
    strategy.run()
