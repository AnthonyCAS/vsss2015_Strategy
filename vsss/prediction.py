import time
from vsss_math.arithmetic import *
from colors import *
from ia.mlp import MLP


class PredictionBase(object):
    def __init__(self, n=10):
        self.t0 = time.time()
        self.N = n
        # Buffer to hold the last N positions
        self.pos_buffer = []
        # Buffer to hold the times of the last N positions
        self.time_buffer = []

    def get_current_time(self, delay=0):
        return time.time()-self.t0-delay

    def update(self, pos, delay):
        self.time_buffer.append(self.get_current_time(delay))
        self.pos_buffer.append(pos.tonp())
        if len(self.pos_buffer) > self.N:
            self.pos_buffer.pop(0)
            self.time_buffer.pop(0)

    def predict(self, deta_time):
        raise NotImplementedError()



class PredictionMru(PredictionBase):
    def predict(self, delta_time):
        """
        Predict delta_time seconds in the future from the last update time
        """
        if len(self.pos_buffer) < 2:
            return self.pos_buffer[-1]
        # average angle
        angles = []
        for i in xrange(len(self.pos_buffer)-1):
            angles.append(angle_to(self.pos_buffer[i], self.pos_buffer[i+1]))
        angle = sum(angles)/len(angles)

        # average velocity
        velocities = []
        for i in xrange(len(self.pos_buffer)-1):
            dt = self.time_buffer[i+1]-self.time_buffer[i]
            velocities.append(distance(self.pos_buffer[i], self.pos_buffer[i+1])/dt)
        velocidadprom = sum(velocities)/len(velocities)

        # final velocity
        dt = self.time_buffer[-1] - self.time_buffer[0]
        d = velocidadprom * dt
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


class PredictionMruv(PredictionBase):
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
            dt = self.time_buffer[i+1]-self.time_buffer[i]
            velocities.append(distance(self.pos_buffer[i], self.pos_buffer[i+1])/dt)
        acelerations = []
        for i in xrange(len(velocities)-1):
            dt = self.time_buffer[i+1]-self.time_buffer[i]
            acelerations.append((velocities[i+1]-velocities[i])/dt)
        aceleration = sum(acelerations)/len(acelerations)
        print aceleration

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


class PredictionANN(PredictionBase):
    def __init__(self, n=10):
        super(PredictionANN, self).__init__(n)
        self.mlp = MLP([1+3*n, 3*n, 2])

    def get_ann_input(self, delta_time):
        temp = [x.tolist() for x in self.pos_buffer]
        for i in xrange(len(temp)):
            temp[i].append(self.time_buffer[i]-self.time_buffer[0])
        temp = [item for sublist in temp for item in sublist]
        return [delta_time] + temp

    def train(self, pos, delay):
        if len(self.pos_buffer) == self.N:
            self.mlp.train(self.get_ann_input(self.get_current_time(delay)-self.time_buffer[0]), pos.tonp()/100)
        self.update(pos, delay)

    def predict(self, delta_time):
        if len(self.pos_buffer) != self.N:
            return np.array([0,0])
        return self.mlp.proc(self.get_ann_input(self.get_current_time()+delta_time-self.time_buffer[0]))*100

        




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
            self.predictor = PredictionMruv(5)

        def strategy(self, data):
            global trajectory, traj_times, traj_screen
            team = data.teams[self.team]
            ball = data.ball

            self.predictor.update(ball, 0.0)
            if trajectory is None:
                trajectory = []
                traj_times = []
                traj_screen = False
                for i in xrange(1,3):
                    trajectory.append(self.predictor.predict(i))
                    traj_times.append(time.time() + i)

            for i in xrange(len(trajectory)):
                if traj_times[i] < time.time():
                    trajectory = []
                    traj_times = []
                    traj_screen = False
                    for i in xrange(1,3):
                        trajectory.append(self.predictor.predict(i))
                        traj_times.append(time.time() + i)
                    break

            out_data = VsssOutData()
            out_data.moves.append(Move())
            out_data.moves.append(Move())
            out_data.moves.append(Move())
            return out_data


    my_color = 0
    strategy = BalonAlArcoStrategy(my_color, 3)
    strategy.run()


if __name__ == "__main__":
    prediction_test()
