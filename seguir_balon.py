import sys

from vsss.serializer import VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.move import Move



class SeguirBalonStrategy(TeamStrategyBase):
    # VISION_SERVER = ('192.168.218.110', 9001)
    latency = 200
    do_visualize = True
    VISION_SERVER = ('0.0.0.0', 9001)
    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('192.168.218.111', 9003)

    serializer_class = VsssSerializerReal

    def set_up(self):
        super(SeguirBalonStrategy, self).set_up()
        self.controller = Controller()

    def strategy(self, data):
        team = data.teams[self.team]
        ball = data.ball
        move = self.controller.go_to_from(ball, team[0])
        out_data = VsssOutData(moves=[move, Move() , Move()])
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
    strategy = SeguirBalonStrategy(my_color, 3)
    strategy.run()
