"""
Find directories
"""

import importlib.resources
import os
import pathlib
import sys
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

import cpop.data
import yaml


def dir_list(pypath: list[str] = None, static: list[str] = None) -> list[pathlib.Path]:
    """
    Return the directories to look for modules in, pypath specifies files
    relative to an installed python package, static is for static dirs
    :param pypath: One or many python paths which will be imported
    :param static: Directories that can be explicitly passed
    """
    ret = set()
    if pypath:
        for path in pypath:
            mod = importlib.import_module(path)
            for m_path in mod.__path__:
                # If we are inside of an executable the path will be different
                ret.add(pathlib.Path(m_path))
    if static:
        ret.update(pathlib.Path(dir_) for dir_ in static)
    return sorted(ret)


def inline_dirs(dirs: Iterable[str], subdir: str) -> list[pathlib.Path]:
    """
    Look for the named subdir in the list of dirs
    :param dirs: The names of configured dynamic dirs
    :param subdir: The name of the subdir to check for in the list of dynamic dirs
    :return An extended list of dirs that includes the found subdirs
    """
    ret = set()
    for dir_ in dirs:
        check = pathlib.Path(dir_) / subdir
        if check.is_dir():
            ret.add(check)
    return sorted(ret)


def dynamic_dirs() -> dict[str, Any]:
    """
    Iterate over the available python package imports and look for configured
    dynamic dirs in pyproject.toml
    """
    dirs = set()
    for dir_ in sys.path:
        if not dir_:
            continue
        path = pathlib.Path(dir_)
        if not path.is_dir():
            continue
        for sub in os.listdir(dir_):
            full = path / sub
            if sub.endswith(".egg-link"):
                with open(full) as rfh:
                    dirs.add(pathlib.Path(rfh.read().strip()))
            elif full.is_dir():
                dirs.add(full)

    # Set up the _dynamic return
    ret = cpop.data.NamespaceDict(
        dyne=cpop.data.NamespaceDict(),
        config=cpop.data.NamespaceDict(),
        imports=cpop.data.NamespaceDict(),
    )

    # Iterate over namespaces in sys.path
    for dir_ in dirs:
        config_file = dir_ / "config.yaml"
        try:
            if not config_file.is_file():
                continue
        except Exception:
            continue
        dynes, configs, imports = parse_config(config_file)
        if dynes:
            cpop.data.update(ret.dyne, dynes, merge_lists=True)
        if configs:
            cpop.data.update(ret.config, configs, merge_lists=True)
        if imports:
            cpop.data.update(ret.imports, imports)

    return ret


def parse_config(
    config_file: str,
) -> tuple[dict[str, object], dict[str, object], set[str]]:
    dyne = defaultdict(lambda: cpop.data.NamespaceDict(paths=set()))
    config = cpop.data.NamespaceDict(
        config=cpop.data.NamespaceDict(),
        cli_config=cpop.data.NamespaceDict(),
        subcommands=cpop.data.NamespaceDict(),
    )
    imports = cpop.data.NamespaceDict()

    config_file = pathlib.Path(config_file)
    if not config_file.is_file():
        return dyne, config, imports
    with open(config_file) as f:
        pop_config = yaml.safe_load(f) or {}

    # Gather dynamic namespace paths for this import
    for name, paths in pop_config.get("dyne", {}).items():
        for path in paths:
            ref = config_file.parent / path.replace(".", os.sep)
            dyne[name]["paths"].add(ref)

    # Get config sections
    for section in ["config", "cli_config", "subcommands"]:
        section_data = pop_config.get(section)
        if not isinstance(section_data, dict):
            continue
        for namespace, data in section_data.items():
            if data is None:
                continue
            config[section].setdefault(namespace, cpop.data.NamespaceDict()).update(
                data
            )

    # Handle python imports
    for imp in pop_config.get("import", []):
        base = imp.split(".", 1)[0]
        if base not in imports:
            imports[base] = importlib.import_module(base)
        if "." in imp:
            importlib.import_module(imp)

    for name in dyne:
        dyne[name]["paths"] = sorted(dyne[name]["paths"])

    return dyne, config, imports
