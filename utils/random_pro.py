import time
from vsss.serializer import VsssSerializerSimulator, VsssSerializerReal
from vsss.strategy import TeamStrategyBase
from vsss.move import Move
from vsss.data import VsssOutData
from numpy.random import uniform

class VisionTestStrategy(TeamStrategyBase):
    use_vision = False
    do_visualize = False
    latency = 150
    print_iteration_time = False

    THIS_SERVER = ('0.0.0.0', 9002)
    CONTROL_SERVER = ('0.0.0.0', 9003)

    serializer_class = VsssSerializerReal
    def set_up(self):
        super(VisionTestStrategy, self).set_up()
        self.last_changes = [time.time()]*3
        self.durations = [0]*3
        self.portero_move = Move(0, 1)
        self.the_moves = [Move(0,0), Move(0,0), self.portero_move]
        self.is_lineal = [0]*3

        self.start_time = time.time()
        self.all_forwards_time = 2

    def all_forwards(self):
        moves = [Move(1.0, 0)]*2 + [self.portero_move]
        return VsssOutData(moves=self.change_order(moves))

    def change_order(self, moves):
        # atacante, atacante, giroloco
        return [moves[0], moves[2], moves[1]]

    def strategy(self, data):
        if time.time() - self.start_time < self.all_forwards_time:
            return self.all_forwards()

        for i in xrange(self.team_size-1):
            if time.time() - self.last_changes[i] > self.durations[i]:
                if not self.is_lineal[i]:
                    self.durations[i] = uniform(0.5, 1.5)
                    ang = uniform(0, 0.1)
                    if uniform() > 0.5:
                        ang = -ang
                    # lineal
                    if uniform() > 0.5:
                        #forwards
                        self.the_moves[i] = Move(1, ang)
                    else:
                        #backwards
                        self.the_moves[i] = Move(-1, ang)
                else:
                    self.durations[i] = uniform(0.1, 0.2)
                    # angular
                    if uniform() > 0.5:
                        # left
                        self.the_moves[i] = Move(0, 1)
                    else:
                        # right
                        self.the_moves[i] = Move(0, -1)

                self.last_changes[i] = time.time()
                self.is_lineal[i] = not self.is_lineal[i]
        return VsssOutData(self.change_order(self.the_moves))



if __name__ == '__main__':
    my_side = 0
    strategy = VisionTestStrategy(my_side, 3)

    strategy.run()
