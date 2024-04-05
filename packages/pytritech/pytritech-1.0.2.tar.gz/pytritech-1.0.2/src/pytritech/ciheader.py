""" The CI Header used at the top of each record in the tritech glf file.

"""
__all__ = ["CIHeader"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"

import struct
import datetime
import pytz
from pytritech.util.time import EpochGem


class CIHeader:
    """The Common interface header. Our GLF Dat file
    contains lots of these that contain various sonar
    data."""

    header_size = 21

    def __init__(self, dat, ids):
        """
        Initialise our CIHeader object.

        Args:
            dat (bytes): A Bytes like file object open for reading.
            ids (int): The offset within dat to start reading from.
        """
        # First character should be an asterix
        assert dat[ids : ids + 1].decode("utf8") == "*"
        # Ignored for now
        # version = int.from_bytes(dat[ids+1:ids+2], 'little')
        self.payload_length = (
            int.from_bytes(dat[ids + 2 : ids + 6], "little") - CIHeader.header_size
        )

        tts = struct.unpack("<d", dat[ids + 6 : ids + 14])[0]
        tseconds = int(tts)
        tmillis = int((tts - tseconds) * 1000)
        itime = EpochGem() + datetime.timedelta(seconds=tseconds, milliseconds=tmillis)

        # Conversion to UTC. Must subtract an hour as the BTC in
        # EpochGem *advances* the clock by one hour as it assumes
        # I'm reading the date as UTC, converting to BST (where it)
        # adds the hour, then we remove that hour by one when we
        # convert back. What we actually want is to read in as BST
        # the convert to UTC and go back an hour.

        # In addition, ALL timedelta operations must be performed
        # BEFORE conversions between timezones as Python has an
        # annoying habit of dropping timezone information when one
        # performs operations on datetime.

        bst = pytz.timezone("Europe/London")
        itime = bst.localize(itime)
        self.time = itime.astimezone(pytz.utc)

        self.type = int.from_bytes(dat[ids + 14 : ids + 15], "little")
        self.device_id = int.from_bytes(dat[ids + 15 : ids + 17], "little")
        self.node_id = int.from_bytes(dat[ids + 17 : ids + 19], "little")
        # Ignored for now
        # spare = dat[ids+19:ids+21]

    def __len__(self):
        return CIHeader.header_size

    def __str__(self):
        return (
            str(self.payload_length)
            + ","
            + str(self.time)
            + ","
            + str(self.type)
            + ","
            + str(self.device_id)
            + ","
            + str(self.node_id)
            + ","
            + str(CIHeader.header_size)
        )
