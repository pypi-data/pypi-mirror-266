import fnmatch
import inspect
import os
import re
import types


def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path and path[-1] == "/":
            path = path[:-1]
    return path


def fileiter(
    top,
    regexp=None,
    wildcard=None,
    info="d",
    relative=False,
    exclude=None,
    neg_reg=None,
    stats=False,
):
    """Iterate over files
    info == 'd'   : returns filename, regexp.groupdict()
    info == 's'   : same, but including mtime and file size
    info == 'g'   : returns filename, regexp.groups()
    info == None: : returns filename

    Allow single expressions or iterator as regexp or wildcard params
    """
    neg_reg = _prepare_test_regext(neg_reg, None)

    include = _prepare_test_regext(regexp, wildcard)
    exclude = _prepare_test_regext(exclude, None)

    if neg_reg and not include:
        include = _prepare_test_regext(".*", None)

    for root, _, files in os.walk(top):
        for name in files:
            filename = os.path.join(root, name)
            if os.path.sep != "/":
                filename = filename.replace(os.path.sep, "/")
            # print(filename)
            if info in ("s",):
                try:
                    st = os.stat(filename)
                except:
                    continue
                stats = {
                    "mtime": st.st_mtime,
                    "size": st.st_size,
                    "blocks": st.st_blocks,
                }
            else:
                stats = {}

            if relative:
                filename = filename.split(top)[-1][1:]

            m3 = _find_match(filename, exclude)
            if m3:
                continue

            m4 = _find_match(filename, neg_reg)
            if m4:
                continue

            m1 = _find_match(filename, include)
            m2 = _find_match(filename, exclude)

            if m1 and not m2:
                m1 = _return_matched_info(m1, info)
                if m1 is not None:
                    m1.update(stats)
                    yield filename, m1
                else:
                    yield filename
            elif m2 and not m1:
                m2 = _return_matched_info(m2, info)
                if m2 is not None:
                    m2.update(stats)
                    yield filename, m2
                else:
                    yield filename

    foo = 1


def file_lookup(pattern, path, appname=""):
    """Search for files in several folders using a strategy lookup.
    - pattern: relative or abspath
    - path: file or directory where to look until if reac
    """
    debug = os.environ.get("DEBUG", False)

    root, name = os.path.split(pattern)
    if root:
        pattern = expandpath(pattern)

    path = path or "."
    if os.path.isabs(pattern):
        candidates, pattern = os.path.split(pattern)
        candidates = [candidates]
    else:
        candidates = [f"/etc/{appname}"]
        # include all folders from stack modules in memory
        stack = inspect.stack()
        while stack:
            dirname = os.path.dirname(stack.pop(0)[0].f_code.co_filename)
            if dirname and dirname not in candidates:
                candidates.append(dirname)

        # include some special folders
        candidates.extend(
            [
                os.path.dirname(__file__),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"),
                f"~/.config/{appname}",
                f"~/{appname}",
                path,
                ".",
            ]
        )
        debug and print(f"CAND: {candidates}")

    # expand all parents for each candidate
    folders = []
    for path in candidates:
        head = tail = expandpath(path)
        ascend = list()
        while tail:
            ascend.append(head)
            head, tail = os.path.split(head)

        ascend.reverse()
        # add only new ones (is faster here that check twice later)
        for path in ascend:
            if path not in folders:
                debug and print(f"+ {path}")
                folders.append(path)

    debug and print(f"FOLD: {folders}")
    for root in folders:
        path = os.path.join(root, pattern)
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if not os.path.exists(path):
            # debug and print(f"not exist:  {path}? - no")
            continue
        debug and print(f"> exists: {path}? - yes")
        yield path


def parse_string(string, regexp=None, wildcard=None, info=None):
    test = _prepare_test_regext(regexp, wildcard)
    m = _find_match(string, test)
    if m:
        return _return_matched_info(m, info)
    return _return_unmatched(info)  # to return compatible values in upper stack


def _prepare_test_regext(regexp=None, wildcard=None, test=None):
    test = test or list()

    if isinstance(regexp, (list, tuple, set)):
        test.extend(regexp)
    else:
        test.append(regexp)

    if not isinstance(wildcard, (list, tuple)):
        wildcard = [wildcard]
    for wc in wildcard:
        if wc and isinstance(wc, str):
            wc = fnmatch.translate(wc)
            test.append(wc)

    test = [re.compile(m).search for m in test if m]

    return test  # you can compile a compiled expression


def _find_match(string, test):
    b_m, b_d = None, {}
    for reg in test:
        if isinstance(reg, types.BuiltinFunctionType):
            m = reg(string)
        else:
            m = reg.search(string)
        if m:
            candidate = m.groupdict()
            if len(candidate) > len(b_d):
                b_m, b_d = m, candidate
            if not candidate and not b_d:
                # print(f"warning: string match but no groups are defined.")
                b_m = m

    return b_m

    # if test:
    # for match in test:
    # m = match(string)
    # if m:
    # return m


def _return_matched_info(m, info):
    if info in ("d", "s"):
        return m.groupdict()
    elif info == "g":
        return m.groups()
    return m.group(0)


def _return_unmatched(info):
    if info in ("d", "s"):
        return dict()
    elif info == "g":
        return list()
