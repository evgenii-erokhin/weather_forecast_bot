class IncorrectStatusCode(Exception):
    pass


class CannotDecodJson(Exception):
    pass


class ConnectionFailed(Exception):
    pass


class DatabaseError(Exception):
    pass


class DatabaseConnectionError(DatabaseError):
    pass


class DuplicateRecordError(DatabaseError):
    pass
