import struct
from .core import Position, RED_TEAM


class VsssInData:
    def __init__(self, teams=None, ball=None):
        if teams is None:
            self.teams = []
        else:
            self.teams = teams
        self.ball = ball


class VsssOutData:
    def __init__(self, moves=None):
        if moves is None:
            self.moves = []
        else:
            self.moves = moves


class VsssSerializer:
    def __init__(self, team_size=3, my_team=RED_TEAM):
        self.team_size = team_size
        self.my_team = my_team

    def load(self, data):
        data = struct.unpack('%sf' % (len(data)/4), data)
        teams = [[], []]
        for color, team in enumerate(teams):
            for i in range(self.team_size):
                team.append(Position(data[3*self.team_size*color + i*3],
                                     data[3*self.team_size*color + i*3+1],
                                     data[3*self.team_size*color + i*3+2]))

        ball = Position(data[2*3*self.team_size],
                        data[2*3*self.team_size + 1])
        return VsssInData(teams, ball)

    def dump(self, out_data):
        data = [float(self.my_team)]
        if len(out_data.moves) != self.team_size:
            print("WARNING: Team size in VsssOutData != Team size in VsssSerializer")
        for move in out_data.moves:
            data.append(move.linvel)
            data.append(move.angvel)
        return struct.pack('%sf' % len(data), *data)
