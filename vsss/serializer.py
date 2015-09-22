import struct

from data import VsssInData, VsssOutData
from position import Position, RobotPosition
from settings import MOVE_BY_POW, MOVE_BY_VEL
from exceptions import MoveTypeError


class VsssSerializerBase(object):
    """
    This is a base class for the serializers that will standardize
    communications between the strategy and differente sources like the
    simulator and the vision system. For this purpose, it will use the
    following clases:
    * VsssInData.
    * VsssOutData.
    """

    def load(self, data):
        """
        Convert raw data to a standard VsssInObject.
        :param data: Raw data comming from simulator or vision system.
        :return: VsssInData object.
        """
        raise NotImplementedError()

    def dump(self, data):
        """
        Convert VsssOutData to raw data that we can send to the simulator or
        the vision system.
        :param data: VsssOutData object.
        :return: Raw data to send to the simulator or vision system.
        """
        raise NotImplementedError()


class VsssSerializerSimulator(VsssSerializerBase):
    """
    This class serializes the communication from/to the simulator.
    """

    def __init__(self, my_team, team_size=3, move_type=MOVE_BY_VEL):
        """
        :param my_team: Which is your team? You can import the teams from
        settings.py.
        :param team_size: How many robots are in your team?
        :param move_type: The type of the VsssOutData to serialize. Can be
        either MOVE_BY_VEL or MOVE_BY_POW.
        :return: None.
        """
        self.team_size = team_size
        self.my_team = my_team
        self.move_type = move_type

    def load(self, data):
        data = struct.unpack('%sf' % (len(data) / 4), data)
        teams = [[], []]
        for color, team in enumerate(teams):
            for i in range(self.team_size):
                team.append(
                    RobotPosition(data[3 * self.team_size * color + i * 3],
                                  data[3 * self.team_size * color + i * 3 + 1],
                                  data[3 * self.team_size * color + i * 3 + 2]))

        ball = Position(data[2 * 3 * self.team_size],
                        data[2 * 3 * self.team_size + 1])
        return VsssInData(teams, ball)

    def dump(self, data):
        assert (type(data) == VsssOutData)
        ret = [float(self.my_team)]
        if len(data.moves) != self.team_size:
            print(
            "WARNING: Team size in VsssOutData != Team size in VsssSerializer")
        for move in data.moves:
            if self.move_type == MOVE_BY_VEL:
                ret.append(move.linvel)
                ret.append(move.angvel)
            elif self.move_type == MOVE_BY_POW:
                ret.append(move.left)
                ret.append(move.right)
            else:
                raise MoveTypeError()
        return struct.pack('%sf' % len(ret), *ret)
