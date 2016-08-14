"""
These classes help us to hold position data which would be computed 
(VsssInData) and turn into VsssOutData positions.

"""


class VsssInData(object):
    """
    This class is meant to hold the income data from the vision system:
    * The position of all the robots of both teams.
    * The position of the ball.
    """

    def __init__(self, teams=None, ball=None):
        """
        :param teams: Array[2], where each item is an array of RobotPositions.
        :param ball: Position object.
        :return: None.
        """
        if teams is None:
            self.teams = []
        else:
            self.teams = teams
        self.ball = ball


class VsssOutData(object):
    """
    This class is meant to hold the out data that we use to command the robots.
    Its basically a list of moves.
    """

    def __init__(self, moves=None):
        """
        :param moves: The list of moves to command my team.
        :return: None.
        """
        if moves is None:
            self.moves = []
        else:
            self.moves = moves
