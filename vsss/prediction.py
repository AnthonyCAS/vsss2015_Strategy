import time
from vsss_math.arithmetic import *
from colors import *

class Prediction(object):
    def __init__(self, n=10):
        self.t0 = time.time()
        self.N = n
        # Buffer to hold the last N positions
        self.pos_buffer = []
        # Buffer to hold the times of the last N positions
        self.time_buffer = []

    def update(self, pos):
        self.time_buffer.append(time.time()-self.t0)
        self.pos_buffer.append(pos.tonp())
        if len(self.pos_buffer) > self.N:
            self.pos_buffer.pop(0)
            self.time_buffer.pop(0)

    def predict(self, delta_time):
        """
        Predict delta_time seconds in the future from the last update time
        """
        if len(self.pos_buffer) < 3:
            return self.pos_buffer[-1]
        # average angle
        angles = []
        for i in xrange(len(self.pos_buffer)-1):
            angles.append(angle_to(self.pos_buffer[i], self.pos_buffer[i+1]))
        angle = sum(angles)/len(angles)

        # average acceleration
        velocities = []
        for i in xrange(len(self.pos_buffer)-1):
            velocities.append(distance(self.pos_buffer[i], self.pos_buffer[i+1]))
        acelerations = []
        for i in xrange(len(velocities)-1):
            acelerations.append(velocities[i+1]-velocities[i])
        aceleration = sum(acelerations)/len(acelerations)

        # final velocity
        d = distance(self.pos_buffer[0], self.pos_buffer[-1])
        t = self.time_buffer[-1] - self.time_buffer[0]
        vf = (d+0.5*aceleration*t*t)/t

        d = vf*delta_time + 0.5*aceleration*delta_time**2
        p = move_by_radius(self.pos_buffer[-1], d, angle)

        if p[0] > 75:
            p[0] = p[0] - 2*(p[0]-75)
        elif p[0] < -75:
            p[0] = p[0] - 2*(p[0]+75)
        elif p[1] > 65:
            p[1] = p[1] - 2*(p[1]-65)
        elif p[1] < -65:
            p[1] = p[1] - 2*(p[1]+65)

        return p






trajectory = None
traj_screen = False
traj_times = None

def prediction_test():
    import sys
    import pygame
    from serializer import VsssSerializerSimulator
    from strategy import TeamStrategyBase
    from data import VsssOutData
    from controller import Controller
    from position import RobotPosition, Position
    from move import Move
    from trajectory import TrajectorySCurve
    from visualizer import VsssVisualizer


    class TrajectoryVisualizer(VsssVisualizer):
        def extra_visualize(self):
            global trajectory, traj_screen
            if trajectory is not None:
                if not traj_screen:
                    trajectory = [self.to_screen(x).tonp() for x in trajectory]
                    traj_screen = True
                if len(trajectory) >= 2:
                    pygame.draw.lines(self.screen, GREEN, False, trajectory, 1)
                for p in trajectory:
                    pygame.draw.circle(self.screen, GREEN, p, 3, 3)



    class BalonAlArcoStrategy(TeamStrategyBase):
        THIS_SERVER = ('0.0.0.0', 9002)
        CONTROL_SERVER = ('0.0.0.0', 9001)
        serializer_class = VsssSerializerSimulator
        do_visualize = True
        visualizer_class = TrajectoryVisualizer

        def set_up(self):
            super(BalonAlArcoStrategy, self).set_up()
            self.controller = Controller()
            self.traj = TrajectorySCurve(r=10)
            self.predictor = Prediction(4)

        def strategy(self, data):
            global trajectory, traj_times, traj_screen
            team = data.teams[self.team]
            ball = data.ball

            if trajectory is None:
                self.predictor.update(ball)
                trajectory = []
                traj_times = []
                traj_screen = False
                for i in xrange(1,3):
                    trajectory.append(self.predictor.predict(i))
                    traj_times.append(time.time() + i)

            self.predictor.update(ball)
            for i in xrange(len(trajectory)):
                if traj_times[i] <= time.time():
                    trajectory = []
                    traj_times = []
                    traj_screen = False
                    for i in xrange(1,3):
                        trajectory.append(self.predictor.predict(i))
                        traj_times.append(time.time() + i)
                    break

            out_data = VsssOutData()
            out_data.moves.append(Move())
            return out_data


    my_color = 0
    strategy = BalonAlArcoStrategy(my_color, 1)
    strategy.run()


if __name__ == "__main__":
    prediction_test()
