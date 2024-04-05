""" Time related support functions """

__all__ = ["EpochGem"]
__version__ = "1.0.1"
__author__ = "Benjamin Blundell <bjb8@st-andrews.ac.uk>"


import datetime

def EpochGem():
    """The Gemini Epoch is slightly different - OS/2 & DOS.
    It's also in BST."""
    epoch_str = "1980-01-01 00:00:00"
    epoch_format = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime(epoch_str, epoch_format)
    return epoch
