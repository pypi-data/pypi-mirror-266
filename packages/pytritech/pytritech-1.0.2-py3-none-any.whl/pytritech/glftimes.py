""" Reading time data from the Tritech Gemini files. 

This module contains the following:
    - glftimes - A faster way to read the GLF time ranges. This is handy if you have many files to read.
    
Examples:

    >>> from glftimes import time_range
    >>> start, end = time_range("path/to/file.glf")

"""

__all__ = ["glf_times"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"


import struct
import pytz
import os
import datetime
import xml.etree.ElementTree as ET
from pytritech.util.time import EpochGem


def glf_times(glf_path: str):
    """Given a path to a GLF file, extract the times from the
    CFG file contained within the uncompressed Zip."""

    with open(glf_path, 'rb') as f:
        glf_file_size = os.path.getsize(glf_path)
        ds = 0

        while ds < glf_file_size:
            file_sig = int(struct.unpack("<I", f.read(4))[0])
            assert file_sig == 0x04034b50

            f.seek(14,1)
            #compressed_file_size = int(struct.unpack("<I", f.read(4))[0])
            _ = int(struct.unpack("<I", f.read(4))[0])
            uncompressed_file_size = int(struct.unpack("<I", f.read(4))[0])
            filename_len = int(struct.unpack("<H", f.read(2))[0])
            extra_field_length = int(struct.unpack("<H", f.read(2))[0])
            filename = str(f.read(filename_len))
            f.seek(extra_field_length, 1)
            f.seek(5, 1) # TODO - this really shouldn't be here but it works! 

            if ".cfg" in filename:
                # we've found the file we need, so read it and return the cfg.
                # We know that this file at any rate is uncompressed.
                cfg = f.read(uncompressed_file_size).decode("utf-8")

                # Need to change a few tags as they are invalid
                cfg = cfg.replace("<0>", "<zero>")
                cfg = cfg.replace("</0>", "</zero>")
                cfg = cfg.replace("<1>", "<one>")
                cfg = cfg.replace("</1>", "</one>")

                root = ET.fromstring(cfg)
                
                start_date_cfg = float(root.find("logHeader/creationTime").text)
                end_date_cfg = float(root.find("logTerminator/closeTime").text)

                bst = pytz.timezone("Europe/London")
                utc = pytz.timezone("UTC")

                tseconds = int(start_date_cfg)
                tmillis = int((start_date_cfg - tseconds) * 1000)
                start_date_cfg = bst.localize(EpochGem() + datetime.timedelta(seconds=tseconds, milliseconds=tmillis))
                start_date_cfg = start_date_cfg.astimezone(utc)

                tseconds = int(end_date_cfg)
                tmillis = int((end_date_cfg - tseconds) * 1000)
                end_date_cfg = bst.localize(EpochGem() + datetime.timedelta(seconds=tseconds, milliseconds=tmillis))
                end_date_cfg = end_date_cfg.astimezone(utc)

                return (start_date_cfg, end_date_cfg)

            else:
                f.seek(uncompressed_file_size, 1)

            ds += 30 + filename_len + extra_field_length + uncompressed_file_size
    
    return None