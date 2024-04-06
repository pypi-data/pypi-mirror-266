"""
Used to scan the given directories for loadable files
"""

import collections
import os
from collections.abc import Iterable
from typing import Any

PY_END = (".py", ".pyc", ".pyo")


def scan(dirs: Iterable[str]) -> dict[str, dict[str, Any]]:
    """
    :param dirs: A list of locations to search for importables files
    :return A description of importable files
    """
    ret = collections.OrderedDict()
    ret["python"] = collections.OrderedDict()
    ret["cython"] = collections.OrderedDict()
    ret["imp"] = collections.OrderedDict()
    for dir_ in dirs:
        for fn_ in os.listdir(dir_):
            _apply_scan(ret, dir_, fn_)
    return ret


def _apply_scan(
    ret: dict[str, dict[str, Any]], dir_: str, fn_: str
) -> dict[str, dict[str, Any]]:
    """
    Convert the scan data into paths and refs
    :param ret: The result of a scan()
    :param dir_:
    :param fn_:
    """
    if fn_.startswith("_"):
        return
    full = os.path.join(dir_, fn_)
    if "." not in full:
        return
    bname = full[: full.rindex(".")]
    if fn_.endswith(PY_END):
        if bname not in ret["python"]:
            ret["python"][bname] = {"path": full}
