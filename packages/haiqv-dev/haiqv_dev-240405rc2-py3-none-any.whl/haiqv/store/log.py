class LogStore:
    __log_level = 'WARN'

    @classmethod
    def __init__(cls, log_level):
        cls.__log_level = log_level

    @classmethod
    def level(cls):
        return cls.__log_level
