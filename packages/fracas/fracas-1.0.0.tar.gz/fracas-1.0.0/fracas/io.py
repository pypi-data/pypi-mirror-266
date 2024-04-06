from datetime import datetime
import re
import os
import sys

from . import config
from . import crypto
from . import dialog


def join(d, display_date=False):
    """Opposite of split().

    Args:
        d (dict): dictionary of journal entries.
        display_date (bool): Use display date format. Default: False.

    Returns:
        journal entries as a string.
    """
    s = ""
    date_format = config.get("date_format")
    for key in sorted(d.keys()):
        body = d[key]
        # Drop blank journal entries.
        if not body.strip():
            continue
        if date_format and display_date:
            isodate = datetime.fromisoformat(key)
            date = datetime.strftime(isodate, date_format)
        else:
            date = key
        s += f"{date}{title(body)}\n\n"
    return s


def read_stdin():
    """If stdin has text, import it and exit.

    Example:
        fracas < file.txt
    """
    # Don't lock console!
    os.set_blocking(0, False)
    s = "".join(sys.stdin.readlines())
    if s:
        d = read()
        imported = split(s)
        d.update(imported)
        write(d)
        print(f"Imported {len(imported.keys())} entries.")
        sys.exit()


def split(s):
    """Split string s into entries at the date stamp.

    Returns:
        dict: datestamp:entry string.
    """
    regex = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
    indices = [m.start(0) for m in re.finditer(regex, s)]
    sections = [s[i:j].strip() for i, j in zip(indices, indices[1:] + [None])]
    return {section[:16]: section[16:].strip() for section in sections}


def title(s):
    """If the first line is < 50 chars, use it as a title.

    Args:
        s (str): journal entry.

    Returns:
        journal entry with title on date stamp line.
    """
    i = s.find("\n")
    if -1 < i < 50:
        return " " + s
    else:
        # Not a title: start on line after date stamp
        return "\n" + s


def read():
    """Read journal file and convert to dictionary."""
    try:
        if config.get("encrypt"):
            with open(config.get("path"), "rb") as f:
                b = f.read()
            pw = dialog.input_password()
            s = crypto.decrypt(b, pw)
        else:
            with open(config.get("path")) as f:
                s = f.read()
        return split(s)
    except FileNotFoundError:
        return {}


def write(d):
    """Convert dictionary to string and write to journal file."""
    s = join(d)
    if config.get("encrypt"):
        b = crypto.encrypt(s)
        with open(config.get("path"), "wb") as f:
            f.write(b)
    else:
        with open(config.get("path"), "w") as f:
            f.write(s)
