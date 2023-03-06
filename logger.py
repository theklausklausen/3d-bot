import logging


class Logger:
    _instance = None

    def __new__(
        cls,
        debug: bool = False
    ):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            super().__init__(cls)
            logging.basicConfig(
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
            )
            cls._instance.debug = debug
            cls._instance.log = logging.getLogger(__name__)
            cls._instance.debug_message('created new logger object')
        else:
            cls._instance.debug_message('return existing logger object')
        return cls._instance

    def debug_message(self, message):
        if self.debug:
            self.log.debug(message)

    def info_message(self, message):
        self.log.info(message)

    def error_message(self, message):
        self.log.error(message)
