class StateMachine:
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.curState = None

    def add_state(self, name, handler):
        name = name.upper()
        self.handlers[name] = handler

    def set_start(self, name):
        self.startState = name.upper()

    def go_to_state(self, name):
        self.curState = name.upper()

    def run(self, cargo):
        if self.curState is None:
            if self.startState is None:
                raise Exception("must call .set_start() before .run()")
            self.curState = self.startState

        ret = None
        while ret is None:
            try:
                handler = self.handlers[self.curState]
            except:
                raise Exception("State " + self.curState + "does not exists")
                ret = handler(cargo)
        return ret