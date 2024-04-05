class ConnectionException(Exception):
    """Raised when trying to access a connection that has not been declared
    """
    def __init__(self) -> None:
        super().__init__("The connection has not been properly set up")


class CursorException(Exception):
    """Raised when trying to access a cursos that has not been declared
    """
    def __init__(self) -> None:
        super().__init__("The Cursor has not been properly set up")


class SelectionException(Exception):
    """Raised when a SELECT query does not starts with 'SELECT'
    """
    def __init__(self) -> None:
        super().__init__("The query does not have the proper format. It should start with a 'SELECT' word")


class GroupException(Exception):
    """Raised when a group column is not in the selected columns
    """
    def __init__(self) -> None:
        super().__init__("Every Group column should be in the ")


class PoolSizeMinException(Exception):
    """Raised when a poolsize smaller than 1 is provided
    """
    def __init__(self) -> None:
        super().__init__("The minium size of a pool is 1")


class MaxOverflowSizeException(Exception):
    """Raised when the max_overflow is smaller than the poolsize
    """
    def __init__(self) -> None:
        super().__init__("The max overflow cannot be smaller than the requested pool")


class DataNotWritten(Exception):
    """Raised when the cursor does not return a rowcount > 0
    """
    def __init__(self, error) -> None:
        super().__init__(f"The data was not correcty inserted into the database. {error}")
