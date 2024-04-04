from datetime import datetime
import re


def parse_uftp_timestamp(timestamp_str):
    """
    Parses a UFTP timestamp into a Python datetime.datetime object. This can take care of the
    """
