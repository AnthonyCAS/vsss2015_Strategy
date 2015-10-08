import sys

from vsss.serializer import VsssSerializerSimulator
from vsss.strategy import TeamStrategySimulatorBase, TeamStrategyBase
from vsss.data import VsssOutData
from vsss.move import Move
from vsss.controller import Controller
from vsss.position import RobotPosition


class BalonAlArcoStrategy(TeamStrategySimulatorBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    VISION_SERVER = ('0.0.0.0', 9001)
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.136', 9003)

    serializer_class = VsssSerializerSimulator

    def set_up(self):
        self.controller = Controller()
        super(BalonAlArcoStrategy, self).set_up()

    def strategy(self, data):
        print 'strategy'
        team = data.teams[self.team]
        ball = data.ball
        out_data = VsssOutData()
        move = self.controller.go_to_from(ball, team[0])
        out_data.moves.append(move)
        return out_data


if __name__ == '__main__':
    def help():
        return """Ejecute el script de cualquiera de las 2 formas, una para cada equipo:
        ./vision_test 0
        ./vision_test 1"""

    # Help the user if he doesn't know how to use the command
    if len(sys.argv) != 2:
        print help()
        sys.exit()
    elif sys.argv[1] != '0' and sys.argv[1] != '1':
        print help()
        sys.exit()

    my_color = int(sys.argv[1])
    strategy = BalonAlArcoStrategy(my_color, 1)
    strategy.run()
