class MoveTypeError(Exception):
    def __init__(self, message):
        if not message:
            message = "Move type can only be vsss.settings.MOVE_BY_VEL or "\
                      "vsss.settings.MOVE_BY_POW"
        super(MoveTypeError, self).__init__(message)
