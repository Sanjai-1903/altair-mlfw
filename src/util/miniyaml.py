"""
miniyaml.py - a TINY YAML reader (standard library only).

Why this exists: Python's standard library has no YAML reader, and we
want zero installs. This handles ONLY the simple subset we use in our
config files:
    key: value
    key:
      - list item
      - another item
    key:
      child: value        (one level of nesting)
Lines starting with '#' and blank lines are ignored.

When the project grows, replace this with the real `pyyaml` package.
"""


def _convert(text):
    # Turn a string into a number or bool when it clearly is one.
    text = text.strip().strip('"').strip("'")
    low = text.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    # try int, then float, else leave as text
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        pass
    return text


def load(path):
    """Read a simple YAML file and return a dict."""
    result = {}
    current_key = None          # the key we are nested under (if any)
    current_list = None         # the list we are filling (if any)

    for raw_line in open(path):
        line = raw_line.rstrip("\n")
        # drop comments and blank lines
        if not line.strip() or line.strip().startswith("#"):
            continue

        indented = line.startswith(" ")
        stripped = line.strip()

        # a list item:  "- something"
        if stripped.startswith("- "):
            if current_list is not None:
                current_list.append(_convert(stripped[2:]))
            continue

        # a "key: value" or "key:" line
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            # drop an inline comment after an UNQUOTED value (e.g. "7  # seed")
            if value and value[0] not in "\"'" and "#" in value:
                value = value.split("#", 1)[0].strip()

            if not indented:
                # top-level key
                current_key = key
                if value == "":
                    # could become a list or a nested map; start as list,
                    # and if a child map line appears we switch to a dict.
                    current_list = []
                    result[key] = current_list
                else:
                    result[key] = _convert(value)
                    current_list = None
            else:
                # nested child under current_key -> make it a dict
                if not isinstance(result.get(current_key), dict):
                    result[current_key] = {}
                    current_list = None
                result[current_key][key] = _convert(value)

    # tidy up: empty lists that were never filled become empty dicts? keep as list
    return result


if __name__ == "__main__":
    import sys
    import pprint
    pprint.pprint(load(sys.argv[1]))
