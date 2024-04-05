""" The ImageRecord from the GLF File.

This module contains the following:

    - ImageRecord - the record of the actual reading from the sonar at a particular time.

"""

__all__ = ["ImageRecord"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"

import datetime
import struct
import pytz
from pytritech.util.time import EpochGem

class ImageRecord:
    """The main image record from the sonar. This starts with a record
    header structure, followed by a GMainImage structure (from the Tritech
    PDF). GMainImage also contains a GImage structure first.

    This ImageRecord object does not contain the binary image data itself,
    but a pointer to where this data lives in the GLF file. The image can be
    retrieved using the GLF object and this ImageRecord object.

    """

    def __init__(self, ciheader, dat, ids):
        """Initialise our ImageRecord object.

        Args:
            ciheader (CIHeader): the CIHeader object that preceeds this record in the GLF file.
            dat (bytes): A Bytes like file object open for reading.
            ids (int): The offset within dat to start reading from.
        """
        self.header = ciheader
        # Start with the Record Header
        ds = ids
        rtype = int.from_bytes(dat[ds : ds + 2], "little")
        assert rtype == 1  # All image records type should be 1
        version = int.from_bytes(dat[ds + 2 : ds + 4], "little")
        assert version == 0xEFEF  # All image records version should be 0xEFEF
        ds += 4

        # Now we are in the GImage Record
        # This is in a different order from what is printed in the datasheet.
        self.image_version = int.from_bytes(dat[ds : ds + 2], "little")
        self.range_start = int(struct.unpack("<I", dat[ds + 2 : ds + 6])[0])
        self.range_end = struct.unpack("<I", dat[ds + 6 : ds + 10])[0]
        self.range_compression = struct.unpack("<H", dat[ds + 10 : ds + 12])[0]
        self.bearing_start = struct.unpack("<I", dat[ds + 12 : ds + 16])[0]
        self.bearing_end = struct.unpack("<I", dat[ds + 16 : ds + 20])[0]
        ds += 20

        self.compression_type = (
            1  # Assume it's not compressed to begin with - TODO - enum!
        )

        # This is only in version 3?
        if self.image_version == 3:
            self.compression_type = struct.unpack("<H", dat[ds: ds + 2])[0]
            ds += 2

        # Actual image data is here.
        csize = int(struct.unpack("<I", dat[ds : ds + 4])[0])
        self.image_data_ptr = ds + 4
        self.image_data_size = csize
        ds += 4 + csize

        # TODO - when reading without zipfile, everything is fine up to here!
        # Continue with GMainImageRecord
        # TODO - We may split GMainImageRecord and GImage eventually
        btsize = self.bearing_end - self.bearing_start
        self.bearing_table = []

        for i in range(0, btsize):
            bearing = struct.unpack("<d", dat[ds + (i * 8) : ds + ((i + 1) * 8)])[0]
            self.bearing_table.append(bearing)

        ds += (btsize * 8)
        self.state_flags = dat[ds : ds + 4]
        self.modulation_freq = struct.unpack("<I", dat[ds + 4 : ds + 8])[0]
        ds += 8

        self.beam_form_app = struct.unpack("<f", dat[ds : ds + 4])[0]
        # This is only guaranteed in milliseconds, not microseconds
        # so do the rounding manually
        tts = struct.unpack("<d", dat[ds + 4 : ds + 12])[0]
        tseconds = int(tts)
        tmillis = int((tts - tseconds) * 1000)
        itime = EpochGem() + datetime.timedelta(seconds=tseconds, milliseconds=tmillis)
        bst = pytz.timezone("Europe/London")
        itime = bst.localize(itime)
        self.db_tx_time = itime.astimezone(pytz.utc)

        self.ping_flags = dat[ds + 12 : ds + 14]
        self.sos_at_xd = struct.unpack("<f", dat[ds + 14 : ds + 18])[0]
        self.percent_gain = struct.unpack("<h", dat[ds + 18 : ds + 20])[0]
        self.chirp = struct.unpack("?", dat[ds + 20 : ds + 21])[0]
        self.sonar_type = int.from_bytes(dat[ds + 21 : ds + 22], "little")
        self.platform = int.from_bytes(dat[ds + 22 : ds + 23], "little")

        #print("iRec", self.db_tx_time, self.chirp, self.sonar_type, self.platform, self.image_version, self.sos_at_xd, self.beam_form_app, self.modulation_freq)

        # For some reason there is an extra byte in here? Word padding?
        # Actually, there seems to be a while lot more!
        endtag = int.from_bytes(dat[ds + 24 : ds + 26], "little")

        assert endtag == 0xDEDE
        ds += 26
        # Assumes the image_data field is still compressed or as it was
        # when the file was read. We uncompress so the 'real' size may
        # be larger, but record size is needed to advance along the
        # catalog so we don't adjust it here.
        self.record_size = ds - ids

        self.image_dim = (
            self.bearing_end - self.bearing_start,
            self.range_end - self.range_start,
        )

        # Check for compression
        if self.image_version != 3:
            exp_size = (self.bearing_end - self.bearing_start) * (
                self.range_end - self.range_start
            )
            if exp_size == self.image_data_size:
                print("Not compressed")
            else:
                # Zlib compression for lower image version
                self.compression_type = 0

    def __len__(self):
        return self.record_size

    def __str__(self):
        return (
            str(self.image_version)
            + ","
            + str(self.range_compression)
            + ","
            + str(self.compression_type)
            + ","
            + str(self.bearing_start)
            + ","
            + str(self.bearing_end)
            + ","
            + str(self.range_start)
            + ","
            + str(self.range_end)
            + ","
            + str(self.state_flags)
            + ","
            + str(self.image_data_size)
            + ","
            + str(self.modulation_freq)
            + ","
            + str(self.beam_form_app)
            + ","
            + str(self.db_tx_time)
            + ","
            + str(self.ping_flags)
            + ","
            + str(self.sos_at_xd)
            + ","
            + str(self.percent_gain)
            + ","
            + str(self.chirp)
            + ","
            + str(self.sonar_type)
            + ","
            + str(self.platform)
            + ","
            + str(self.record_size)
        )
