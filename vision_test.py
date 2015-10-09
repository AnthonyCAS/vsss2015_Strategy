from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase


class VisionTestStrategy(TeamStrategyBase):
    use_control = False
    do_visualize = True

    THIS_SERVER = ('0.0.0.0', 9002)

    serializer_class = VsssSerializerSimulator

    def strategy(self, data):
        print data.teams


if __name__ == '__main__':
    my_color = 0
    strategy = VisionTestStrategy(my_color, 1)

    strategy.run()
