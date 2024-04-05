""" Calculate the range in metres of the image."""

__all__ = ["calculate_range"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <me@benjamin.computer>"

from pytritech.image import ImageRecord

def calculate_range(img_rec: ImageRecord) -> float:
    """ Calculate the range the sonar was set to when it took
    this image (in metres)."""
    rangeCompUsed = 0
    
    if img_rec.range_compression & 0x20:
        # Absolute compression level
        rangeCompUsed = (img_rec.range_compression & 0x0F)
    else:
        # Encoded compression level
        rangeCompUsed = (1 << (img_rec.range_compression & 0x000F))
 
    RangeLines = float(img_rec.range_end) / float(rangeCompUsed)
    ModulationFreq= float(img_rec.modulation_freq) / float(rangeCompUsed)

    rangeInMeters = ( RangeLines * (img_rec.sos_at_xd / 2.0) / ModulationFreq)
    return rangeInMeters
