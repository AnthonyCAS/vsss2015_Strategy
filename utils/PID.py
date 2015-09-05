class PID:
    def __init__(self, kp, kd, ki):
        self.Kp = kp
        self.Kd = kd
        self.Ki = ki
        self.prev_error = 0
        self.cum_error = 0

    def update(self, error):
        P = self.Kp * error
        D = self.Kd * (error - self.prev_error)
        self.prev_error = error
        self.cum_error += error
        I = self.Ki * self.cum_error
        return P + I + D
