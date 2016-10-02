import struct
import numpy as np

from data import VsssInData, VsssOutData
from position import RobotPosition, Position


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
        Convert raw data to a standard VsssInObject. For positions, it will use
        the center of the field as (0,0)
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


class VsssSerializerReal(VsssSerializerBase):
    """
    This class serializes the communication from/to the simulator.
    """

    def load(self, data):
        data = struct.unpack('%sf' % (len(data) / 4), data)
        assert(len(data) == 20)
        # print data
        teams = [[], []]
        for i, team in enumerate(teams):
            for robot in range(3):
                team.append(
                    RobotPosition(data[9 * i + robot * 3],
                                  data[9 * i + robot * 3 + 1],
                                  data[9 * i + robot * 3 + 2])
                )
        ball = Position(data[18], data[19])
        return VsssInData(teams[0], teams[1], ball)

    def dump(self, data):
        assert(type(data) == VsssOutData)
        assert(len(data.moves) == 3)
        ret = []
        for move in data.moves:
            ret.append(move.linvel)
            ret.append(move.angvel)
        return struct.pack('%sf' % len(ret), *ret)
