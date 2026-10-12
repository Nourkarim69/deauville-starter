class FestivalError(Exception):
    pass


class NotFoundError(FestivalError):
    pass


class ConflictError(FestivalError):
    pass


class InvalidValueError(FestivalError):
    pass