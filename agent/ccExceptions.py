#!/usr/bin/python

class Error(Exception):
    """Base class for exceptions """
    pass


class BlockError(Error):
    """Raised when Block processing fails.  Rollback not required

    Attributes:
        reason -- what caused the block to fail (eg instruction that is invalid)
        id -- id of the block that failed
        previous -- id of the previous block this failed block points to
    """

    def __init__(self, reason, id, previous):
        self.reason = reason
        self.id = id
        self.previous = previous

class RedisError(Exception):
    """Raised when redis encounters an error because it cannot 'get' find a value

    Attributes:
        reason -- what redis cannot find
    """

    pass
