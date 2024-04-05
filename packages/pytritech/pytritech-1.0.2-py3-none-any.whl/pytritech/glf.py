""" Reading data from the Tritech Gemini files. 

This module contains the following:
    - GLF - The GLF class representing a GLF file
    
Examples:

    >>> from glf import GLF
    >>> glfobj = GLF("path/to/file.glf")
    >>> record = glfobj.images[0]
    >>> bitmap, dims = glfobj.extract_image(record)

"""

__all__ = ["GLF"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"

from typing import Tuple
from zipfile_isal import ZipFile
from isal import isal_zlib
import xml.etree.ElementTree as ET
from pytritech.ciheader import CIHeader
from pytritech.image import ImageRecord
from pytritech.status import StatusRecord


class GLF:
    """A class that represents the GLF file. We hold the various records
    in order with headers and values, but not the raw image/sonar data.
    We hold pointers to these into the GLF file."""

    # TODO - potentially join multiple GLF files together?
    # TODO - potentially keep all files as zlib.IO pointers and keep them all open?

    def __init__(self, glfpath: str):
        """Initialise our glf object.

        Args:
            glfpath (str): full path and name of the glf file.
        """
        self.filepath = glfpath
        self._zobject = None
        self.config = None
        self.images = None
        self.dat = None # Keep the whole dat in memory if we can
        self.status = None
        self.statuses = []

    def _read_config(self):
        """Return the config file as an element tree xml parsed2."""
        for zname in self._zobject.namelist():
            # Look for the config file
            if ".cfg" in zname:
                with self._zobject.open(zname) as f:
                    cfg = f.read().decode("utf-8")
                    # Need to change a few tags as they are invalid
                    cfg = cfg.replace("<0>", "<zero>")
                    cfg = cfg.replace("</0>", "</zero>")
                    cfg = cfg.replace("<1>", "<one>")
                    cfg = cfg.replace("</1>", "</one>")

                    root = ET.fromstring(cfg)
                    self.config = root

        # Set some useful parameters on the GLF class such as sonar_id and range
        # TODO - it turns out that the range text doesn't always exist and there may be multiple ones
        #self.sonar_ids = []

        # This method appears not to work
        #for sonar_node in root.find("GuiCurrentSettings/devices"):
        #    self.sonar_ids.append(int(sonar_node.find("id").text))

    
    def __enter__(self):
        self._zobject = ZipFile(self.filepath, "r")
        
        for zname in self._zobject.namelist():
            if ".dat" in zname:
                self._f = self._zobject.open(zname)
        
        self._read_config()
        # We've read the config so we should be at the image_records
        self._parse_dat()

        return self

    def __exit__(self, *args):
        self._zobject.close()
        del self.dat
   

    def extract_image(self, image_rec: ImageRecord) -> Tuple[bytes, Tuple[int, int]]:
        """Return the data for the image, along with the dimensions -
        (bearing, range).

        Args:
            image_rec (ImageRecord): The record for which we want the bitmap

        Returns:
            Tuple: A tuple of bytes, and a tuple of (int, int) for height x width

        """
        image_data = None

        ptr = image_rec.image_data_ptr
        #self._f.seek(ptr)
        #image_data = self._f.read(image_rec.image_data_size)
        image_data = self.dat[ptr:ptr+image_rec.image_data_size]

        if image_rec.compression_type == 0:
            image_data = isal_zlib.decompress(image_data)
        elif image_rec.compression_type == 2:
            print("H264 decompression not yet implemented.")
            assert False

        return image_data, image_rec.image_dim

    def _parse_dat(self):
        """Read the dat file stored inside the glf which uses Zip."""
        self.images = []
        self.sonar_ids = []
        self.dat = self._f.read()
        file_offset = 0

        # We should get towards the last bytes, both of which
        # should be DEDE
        while file_offset < len(self.dat) - 2:
            header = CIHeader(self.dat, file_offset)
            file_offset += len(header)

            if header.type == 0:
                # image record
                image_rec = ImageRecord(header, self.dat, file_offset)
                self.images.append(image_rec)
                file_offset += len(image_rec)

                # Add sonar IDs here as we find them. Seems the best way.
                sonar_id = image_rec.header.device_id

                if sonar_id not in self.sonar_ids:
                    self.sonar_ids.append(sonar_id)

            elif header.type == 1:
                # V4 protocol
                assert False
                break
            elif header.type == 2:
                # analog video
                assert False
                break
            elif header.type == 3:
                # Gemini Status
                status_rec = StatusRecord(header, self.dat, file_offset)
                self.statuses.append(status_rec)
                file_offset += len(status_rec)
            elif header.type == 98:
                # Raw Serial
                assert False
                break
            elif header.type == 99:
                # Generic
                assert False
                break

        assert (
            int.from_bytes(self.dat[file_offset : file_offset + 2], "little")
            == 0xDEDE
        )
