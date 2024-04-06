from enum import IntFlag


class ConnectionState(IntFlag):
    """
    Enumerates connection state types.
    """

    # Connection is not made for the meter.
    NONE = 0
    # Connection is made for HDLC level.
    HDLC = 1
    # Connection is made for DLMS level.
    DLMS = 2
