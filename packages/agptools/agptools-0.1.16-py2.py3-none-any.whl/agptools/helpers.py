from datetime import timedelta
import os
import re
import string
import sys
from typing import Any, Callable, List
import uuid
import yaml

from dateutil import parser
from glom import glom, assign


# ------------------------------------------------
# Select the best of a serie using a score function
# ------------------------------------------------
def best_of(data: List[Any], func: Callable, *args, **kw) -> List:
    """
    Select the best of a series using a score function

    Callable may return a score or (score, item to be saved)

    If only score is returned, then current item will be saved
    as best candidate
    """
    best_score, best_result = sys.float_info.min, None
    for item in data:
        result = func(item, *args, **kw)
        if isinstance(result, (tuple, list)) and len(result) == 2:
            score, result = result
        else:
            score, result = result, item

        if best_score < score:
            best_score, best_result = score, result
    return best_score, best_result


# ------------------------------------------------
# File and config helpers
# ------------------------------------------------
def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path[-1] == "/":
            path = path[:-1]
    return path


def load_config(env):
    """Merge config files"""
    cfg = env.__dict__
    for path in reversed(env.config_files):
        try:
            data = yaml.load(open(path, "rt", encoding="utf-8"), Loader=yaml.Loader)
            # merge(cfg, data, inplace=True) # use any deep merge library or ...
            cfg.update(data)

        except FileNotFoundError:
            pass

    env.folders = {expandpath(p): None for p in env.folders}


def save_config(env):
    os.makedirs(os.path.dirname(env.config_file), exist_ok=True)
    yaml.dump(env.__dict__, open(env.config_file, "wt"))


# -----------------------------------------------------------
# URI handling
# -----------------------------------------------------------
reg_uri = re.compile(
    """(?imsx)
    (?P<fservice>
        (
            (?P<fscheme>
                (?P<direction>[<|>])?(?P<scheme>[^:/]*))
                ://
        )?
        (?P<xhost>
           (
                (?P<auth>
                   (?P<user>[^:@/]*?)
                   (:(?P<password>[^@/]*?))?
                )
            @)?
           (?P<host>[^@:/?]*)
           (:(?P<port>\d+))?
        )
    )?
    (?P<path>/[^?]*)?
    (\?(?P<query>[^#]*))?
    (\#(?P<fragment>.*))?
    """
)


def parse_uri(uri, bind=None, drop_nones=False, default=None, **kw):
    """Extended version for parsing uris:

    Return includes:

    - *query_*: dict with all query parameters splited

    If `bind` is passed, *localhost* will be replace by argument.

    """

    m = reg_uri.match(uri)
    if m:
        for k, v in m.groupdict(default=default).items():
            if k not in kw or v is not None:
                kw[k] = v
        if bind:
            kw["host"] = kw["host"].replace("localhost", bind)
        if kw["port"]:
            kw["port"] = int(kw["port"])
            kw["address"] = tuple([kw["host"], kw["port"]])
        if kw["query"]:
            kw["query_"] = dict(parse.parse_qsl(kw["query"]))

        kw["uri"] = uri

    if drop_nones:
        kw = {k: v for k, v in kw.items() if v is not None}
    return kw


def build_uri(
    fscheme="",
    direction="",
    scheme="",
    xhost="",
    host="",
    port="",
    path="",
    query="",
    fragment="",
    query_={},
    **kw,
):
    """Generate a URI based on individual parameters"""
    uri = ""
    if fscheme:
        uri += fscheme or ""
    else:
        if not direction:
            uri += scheme or ""
        else:
            uri += f"{direction}{scheme or ''}"
    if uri:
        uri += "://"

    if xhost:
        uri += xhost
    else:
        host = host or f"{uuid.getnode():x}"
        uri += host
        if port:
            uri += f":{port}"

    if path:
        uri += f"{path}"

    if query_:
        # query_ overrides query if both are provided
        query = "&".join([f"{k}={v}" for k, v in query_.items()])

    elif isinstance(query, dict):
        query = "&".join([f"{k}={v}" for k, v in query.items()])

    if query:
        uri += f"?{query}"
    if fragment:
        uri += f"#{fragment}"

    return uri


# --------------------------------------------------
#  Convert Base
# --------------------------------------------------

# CHAR_LOOKUP = list(string.digits + string.ascii_letters)

#  avoid use of numbers (so can be used as regular attribute names with ".")
CHAR_LOOKUP = list(string.ascii_letters)
INV_LOOKUP = {c: i for i, c in enumerate(CHAR_LOOKUP)}


def convert_base(number, base, padding=-1, lookup=CHAR_LOOKUP) -> str:
    """Coding a number into a string in base 'base'

    results will be padded with '0' until minimal 'padding'
    length is reached.

    lookup is the char map available for coding.
    """
    if base < 2 or base > len(lookup):
        raise RuntimeError(f"base: {base} > coding map length: {len(lookup)}")
    mods = []
    while number > 0:
        mods.append(lookup[number % base])
        number //= base

    while len(mods) < padding:
        mods.append(lookup[0])

    mods.reverse()
    return "".join(mods)


def from_base(key, base, inv_lookup=INV_LOOKUP):
    """Convert a coded number in base 'base' to an integer."""
    number = 0
    keys = list(key)
    keys.reverse()
    w = 1
    for c in keys:
        number += INV_LOOKUP[c] * w
        w *= base
    return number


# def new_uid(base=50):
# number = uuid.uuid1()
# return convert_base(number.int, base)
SEED = 12345


def new_uid(base=50):
    global SEED
    SEED += 1
    return convert_base(SEED, base)


# ------------------------------------------------
# File and config helpers
# ------------------------------------------------
def replace(text):
    text = str(text)
    text = text.lower()
    text = text.replace("á", "a")
    text = text.replace("é", "e")
    text = text.replace("í", "i")
    text = text.replace("ó", "o")
    text = text.replace("ú", "u")
    return text


# from xml.sax.saxutils import escape
# ------------------------------------------------
# jinja2 filters
# ------------------------------------------------
def escape(text: str):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


def fmt(value, fmt=">40"):
    fmt = "{:" + fmt + "}"
    try:
        value = fmt.format(value)
    except:
        pass
    return value


# ------------------------------------------------
# glom extensions
# ------------------------------------------------
def setdefault(obj, path, val, missing=dict):
    current = glom(obj, path, default=None)
    if current is None:
        assign(obj, path, val, missing=missing)
        return val
    return current


# ------------------------------------------------
# Converter functions
# ------------------------------------------------


def I(x):
    return x


def INT(x):
    if x is not None:
        return int(x)
    return x


def FLOAT(x):
    if x is not None:
        return float(x)
    return x


def BOOL(x):
    if isinstance(x, str):
        return x.lower() in ("true", "yes")
    return bool(x)


def TEXT(x):
    if x is not None:
        return x.text
    return x


def STRIP(x):
    if x is not None:
        return x.strip()


def DATE(x):  # TODO
    if x is not None:
        if isinstance(x, str):
            return parser.parse(x)
    return x


def DURATION(x):  # TODO
    if x is not None:
        return timedelta(days=float(x))


def COLOR(x):
    """Task color
    Ignore when if a "black" or "blue" color and let GP
    use default ones next time.
    """
    if x not in ("#8cb6ce", "#000000"):
        return x
    return x  # TODO: remove, this hack will remove default colors


def PRIORITY(x):
    """GanttProject PRIORITY.... (have not sense :) )"""
    return {
        "3": -2,  #  Lowest
        "0": -1,  #  Low
        None: 0,  #  Normal (missing)
        "2": 1,  #  High
        "4": 2,  #  Highest
    }.get(x, 0)


# ------------------------------------------------
# console
# ------------------------------------------------

GREEN = "\033[32;1;4m"
RESET = "\033[0m"


last_sepatator = 40


def banner(
    header,
    lines=None,
    spec=None,
    sort_by=None,
    sort_reverse=True,
    output=print,
    color=GREEN,
):
    global last_sepatator
    lines = lines or []
    # compute keys spaces
    m = 1 + max([len(k) for k in lines] or [0])
    if isinstance(lines, dict):
        if sort_by:
            idx = 0 if sort_by.lower().startswith("keys") else 1
            lines = dict(
                sorted(
                    lines.items(),
                    key=lambda item: item[idx],
                    reverse=sort_reverse,
                )
            )
        _lines = []
        for k, v in lines.items():
            if spec:
                try:
                    v = glom(v, spec)
                except:
                    v = getattr(v, spec)

            line = f"{k.ljust(m)}: {v}"
            _lines.append(line)
        lines = _lines

    if lines:
        m = max([len(l) for l in lines])
        last_sepatator = m
    elif last_sepatator:
        m = last_sepatator
    else:
        m = max([40, len(header)]) - len(header) + 1

    # m = max([len(l) for l in lines] or [40, len(header)]) - len(header) + 1
    output(f"{color}{header}{' ' * m}{RESET}")
    for line in lines:
        output(line)
