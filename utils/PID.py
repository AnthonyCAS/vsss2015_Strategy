class PID:
    """ La clase PID, implementa un mecanismo de control, Proportional, Integral Derivative controller
        Se basa en el cálculo de los errores entre los valores medidos y los valores
        deseados.
    """
    def __init__(self, kp, kd, ki):
        self.Kp = kp
        self.Kd = kd
        self.Ki = ki
        self.prev_error = 0
        self.cum_error = 0
        """
            KP:
                constante proporcional
            Kd:
                constante derivativa
            Ki:
                constante integral
        """
    #salida: suma de la parte proporcional, derivativa e integral.
    def update(self, error):
        P = self.Kp * error
        D = self.Kd * (error - self.prev_error)
        self.prev_error = error
        self.cum_error += error
        I = self.Ki * self.cum_error
        return P + I + D
