import datetime
import re
import subprocess
import tempfile

from . import config
from . import io


def contains(s, terms):
    """Return True if string s contains all terms.

    Args:
        s (str): journal entry body.
        terms (list): keywords or tags.

    Note:
        tags require whole word search: #blue-mountain and #blue are two
        different tags with different meanings. But if you're searching
        for the keyword blue, returning blue or blue-mountain is useful.
    """
    keywords = [t for t in terms if not t.startswith("#")]
    tags = [t for t in terms if t.startswith("#")]
    for tag in tags:
        regex = re.compile(r"\B" + tag + r"\b", re.IGNORECASE)
        if not regex.search(s):
            return False
    for keyword in keywords:
        regex = re.compile(keyword, re.IGNORECASE)
        if not regex.search(s):
            return False
    return True


def diff(d1, d2):
    """Compare two dictionaries.

    Args:
        d1 (dict)
        d2 (dict)

    Returns:
        string with totals for add, modify, delete.
    """
    d1_keys = d1.keys()
    d2_keys = d2.keys()
    added = len(d2_keys - d1_keys)
    deleted = len(d1_keys - d2_keys)
    modified = 0
    for key in d1_keys:
        if key in d2_keys and d1[key] != d2[key]:
            modified += 1
    return f"{modified} modified, {deleted} deleted, {added} added."


def edit(args):
    """Edit selected entries.

    Args:
        args (Namespace): ArgumentParser Namespace.

    Returns:
        string with add, delete, modify count.
    """
    d = io.read()
    d_in_range = search_date_range(d, args)
    d_found = find(d_in_range, args.search_terms)
    dn = get_last_n(d_found, args)
    # Delete entries to be edited. Will be added after editing.
    for key in dn.keys():
        del d[key]
    s_in = io.join(dn)
    s_out = edit_file(s_in)
    d_out = io.split(s_out)
    # Update dict with edited entries.
    d.update(d_out)
    io.write(d)
    return diff(dn, d_out)


def edit_file(s=""):
    """Edit file.

    Args:
        s (str): text file input string. Default: ''.

    Returns:
        Output string.
    """
    with tempfile.NamedTemporaryFile() as fp:
        if s:
            with open(fp.name, mode="w") as f:
                f.write(s)
        subprocess.call([config.get("editor"), fp.name])
        with open(fp.name, mode="r") as f:
            s_out = f.read().strip()
    return s_out


def get_last_n(d, args):
    """Get last (n) entries.

    Args:
        d (dict): dictionary of journal entries.
        args (Namespace): ArgumentParser Namespace.

    Returns:
        dict of journal entries.
    """
    if not getattr(args, "n", None):
        return d
    keys = sorted(d.keys())[-args.n :]
    return {k: d[k] for k in keys}


def search_date_range(d, args):
    """Find journal entries within date range.

    Args:
        d (dict): dictionary of journal entries.
        args (Namespace): ArgumentParser Namespace.

    Returns:
        dict of journal entries within date range.
    """
    in_range = {}
    date_format = "%Y-%m-%d %H:%M"
    for key in d:
        if args.to_date:
            validate(args.to_date)
            if args.to_date < key:
                continue
        if args.from_date:
            validate(args.from_date)
            if args.from_date > key:
                continue
        in_range[key] = d[key]
    return in_range


def print_contains(args):
    """Print entries w/ keywords.

    Args:
        args (Namespace): ArgumentParser Namespace.
    """
    d = io.read()
    dd = search_date_range(d, args)
    found = find(dd, args.search_terms)
    if found:
        print(io.join(found, display_date=True))
    else:
        print("Not found")


def print_last_n(args):
    """Print last (n) entries."""
    d = io.read()
    lastn = get_last_n(d, args)
    print(io.join(lastn, display_date=True))


def print_tag_table():
    """Print list of tag:count."""
    d = io.read()
    tag_counts = get_tag_count(d)
    MIN_COLUMN_WIDTH = 7
    column_width = max([len(k) for k in tag_counts])
    max_width = str(max(column_width, MIN_COLUMN_WIDTH))
    column = "{:>" + max_width + "} {:>" + max_width + "}"
    print(column.format("Tag", "Count"))
    for key in sorted(tag_counts.keys()):
        print(column.format(key, tag_counts[key]))


def find(d, terms):
    """Find journal entries containing keywords or tags.

    Args:
        d (dict): dictionary of journal entries.
        terms (list): keywords or tags to search for.

    Returns:
        dictionary of journal entries.
    """
    return {k: v for k, v in d.items() if contains(v, terms)}


def get_tag_count(d):
    """Return dict of tag:count found in journal.

    Args:
        d (dict): dictionary of journal entries.

    Returns:
        dictionary: tag:count.
    """
    s = "\n".join([v for v in d.values()])
    regex = re.compile(r"\B#[\w-]+\b", re.IGNORECASE)
    counts = dict()
    for tag in re.findall(regex, s):
        tag = tag.lower()
        counts[tag] = counts.get(tag, 0) + 1
    return counts


def compose():
    """Compose a single journal entry."""
    d = io.read()
    s = edit_file()
    if s:
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        d[time_stamp] = s
        io.write(d)


def main(args):
    config.read()
    if args.edit:
        changes = edit(args)
        print(changes)
    elif args.search_terms:
        print_contains(args)
    elif args.n:
        print_last_n(args)
    elif args.tags:
        print_tag_table()
    elif args.to_date or args.from_date:
        print_contains(args)
    else:
        # fracas < import.txt?
        io.read_stdin()
        compose()


def validate(s):
    """Raise ValueError if s isn't a valid date or datetime."""
    if ":" in s:
        try:
            datetime.datetime.strptime(s, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("Datetime format must be YYYY-MM-DD HH:MM")
    else:
        try:
            datetime.datetime.strptime(s, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD")
    return True
