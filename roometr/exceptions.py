class RoometrException (BaseException):
    pass


class RoometrDeveloperNotFound(RoometrException):
    pass


class RoometrComplexNotFound(RoometrException):
    pass


class RoometrHouseNotFound(RoometrException):
    pass


class RoometrApptNotFound(RoometrException):
    pass


class Roometr404Exception(RoometrException):
    pass


class Roometr403Exception(RoometrException):
    pass


class RoometrBadServerResponseException(RoometrException):
    pass
