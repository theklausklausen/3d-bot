from logger import Logger


class Job():
    _instance = None

    def __new__(
        cls,
        estimated_print_time=None,
        file=None,
        completion=None,
        print_time_left=None,
        print_time=None,
        state=None,
        debug=False
    ):
        if cls._instance is None:
            cls._instance = super(Job, cls).__new__(cls)
            super().__init__(cls)
            cls._instance.logger = Logger(debug=debug)
            cls._instance.estimated_print_time = estimated_print_time
            cls._instance.file = file
            cls._instance.progress = {
                'completion': completion,
                'print_time_left': print_time_left,
                'print_time': print_time
            }
            cls.states = {
                25: None,
                50: None,
                75: None,
                100: None
            }
            cls.state = state
            cls.lastState = None
            cls._instance.logger.debug_message('created new job object')
        else:
            cls._instance.logger.debug_message('return existing job object')
            cls._instance.estimated_print_time = estimated_print_time
            cls._instance.file = file
            cls._instance.progress = {
                'completion': completion,
                'print_time_left': print_time_left,
                'print_time': print_time
            }
            cls._instance.lastState = cls._instance.state
            cls._instance.state = state
        return cls._instance

    def __del__(self):
        self.logger.info_message('deleting job instance')

    def has_quarter_achieved(self) -> bool:
        for key, value in enumerate(self.states):
            if int(self.progress['completion']) >= int(value) and self.states[value] is None:
                self.logger.debug_message('set state {state} to {value}'.format(
                    state=value, value=self.progress['completion']))
                self.states[value] = float(self.progress['completion'])
                return True
        return False

    def has_paused(self) -> bool:
        return self.state == 'Paused' and self.state != self.lastState

    def has_finished(self) -> bool:
        return self.states[100] is not None
