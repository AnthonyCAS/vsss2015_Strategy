import sys

from vsss.serializer import VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.data import VsssOutData
from vsss.controller import Controller
from vsss.move import Move
from vsss.position import Position


class SeguirBalonStrategy(TeamStrategyBase):
    latency = 0
    do_visualize = True
    serializer_class = VsssSerializerReal

    def set_up(self):
        super(SeguirBalonStrategy, self).set_up()
        # self.controller = Controller()

    def strategy(self, data):
        print "my team", data.my_team
        print "opp team", data.opp_team
        print "ball", data.ball
        # team = data.teams[self.team]
        # ball = data.ball
        # goal = Position(50, 50)
        # move = self.controller.go_to_from(goal, team[0])
        # print move
        # out_data = VsssOutData(moves=[move, Move(0, 0), Move(0, 0)])
        # return out_data


if __name__ == '__main__':
    strategy = SeguirBalonStrategy()
    strategy.run()
