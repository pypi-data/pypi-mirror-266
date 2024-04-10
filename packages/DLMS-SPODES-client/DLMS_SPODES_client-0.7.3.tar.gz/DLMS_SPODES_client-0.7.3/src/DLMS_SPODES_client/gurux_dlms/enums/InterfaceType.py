from enum import IntEnum


class InterfaceType(IntEnum):
    """InterfaceType enumerates the usable types of connection in GuruxDLMS."""
    HDLC = 0
    WRAPPER = 1
    PDU = 2
    WIRELESS_MBUS = 3
