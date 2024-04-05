class NoneError(Exception):
    pass


class Guard:

    @staticmethod
    def against_null(value):
        if value is not None:
            return value
        raise NoneError()

