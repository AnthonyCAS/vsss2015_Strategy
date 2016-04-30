class PID(object):
    """
    PID: Stands for Proportional Integrative Derivative. It receives the error
    in each iteration and calculates the control variable.

    For example to calculate the angular velocity (control variable), it
    receives the angle that the robot needs to turn to point to its
    target (error).
    """

    def __init__(self, kp, ki, kd):
        """
        :param kp: Proportional constant.
        :param ki: Integrative constant.
        :param kd: Derivative constant.
        :return: None.
        """
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd
        self.prev_error = 0
        self.cum_error = 0

    def update(self, error):
        """
        This function should be called at every tick to update the control
        variable.
        :param error: The error in the current tick.
        :return: The control variable for the current tick.
        """
        P = self.Kp * error
        self.cum_error += error
        I = self.Ki * self.cum_error
        D = self.Kd * (error - self.prev_error)
        self.prev_error = error
        return P + I + D
