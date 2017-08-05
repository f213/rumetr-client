class RoometrException (Exception):
    pass


class RoometrDeveloperNotFound(Exception):
    pass


class Roometr404Exception(RoometrException):
    pass


class Roometr403Exception(RoometrException):
    pass


class RoometrBadServerResponseException(RoometrException):
    pass
