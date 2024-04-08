"""
Load the files detected from the scanner
"""

import asyncio
import importlib.machinery
import importlib.util
import inspect
import os
import sys
import types
from collections.abc import Callable
from typing import Any
from typing import List

import cpop.contract
import cpop.data
import pop.exc

BASE_TYPES = (int, float, str, bytes, bool, type(None))


class LoadError(Exception):
    """
    Errors from the loader are contained herein
    """

    __slots__ = ("edict", "traceback")

    def __init__(self, msg, exception=None, traceback=None, verror=None):
        self.edict = {
            "msg": msg,
            "exception": exception,
            "verror": verror,
        }
        self.traceback = traceback

    def __call__(self):
        """
        Return the error cases
        """
        return self.edict

    def __getattr__(self, attr):
        """
        Return a lambda that returns the edict
        """
        return self.__calling_load_error__


def load_mod(modname: str, form: str, path: str) -> "LoadedMod":
    """
    Load a single module
    :param modname: The name of the module to get from the loader
    :param form: The name of the loader module
    :param path: The package to use as the anchor point from which to resolve the
        relative import to an absolute import.
    """
    this = sys.modules[__name__]
    return getattr(this, form)(modname, path)


def python(modname: str, path: str) -> "LoadedMod" or LoadError:
    """
    Attempt to load the named python modules
    :param modname: The name of the module to get from the loader
    :param path: The package to use as the anchor point from which to resolve the
        relative import to an absolute import.
    """
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    module.__file__ = path
    spec.loader.exec_module(module)
    return module


def _base_name(bname: str, mod: "LoadedMod") -> tuple[str, str]:
    """
    Find the basename and alias of a loader module
    :param bname: The base name of the mod's path
    :param mod: A loader module or a LoadError if the module didn't load
    """
    base_name = os.path.basename(bname)
    return base_name, getattr(mod, "__virtualname__", base_name)


async def _load_virtual(
    hub: "pop.hub.Hub",
    mod: "LoadedMod" or LoadError,
    bname: str,
    vtype: str,
) -> dict[str, Any]:
    """
    Run the virtual function to name the module and check for all loader
    errors
    :param hub: The redistributed pop central hub
    :param virtual: Toggle whether or not to process __virtual__ functions
    :param mod: A loader module or a LoadError if the module didn't load
    :param bname: The base name of the mod's path
    :param vtype: The name of the virtual function to call on the module I.E. __virtual__ or __sub_virtual__
    """
    base_name, name = _base_name(bname, mod)

    if not hasattr(mod, vtype):
        # No __virtual__ processing is required.
        # Return the mod's name as the defined __virtualname__ if defined,
        # else, the base_name
        return {"name": name}

    try:
        vret = await getattr(mod, vtype)(hub)
    except Exception as e:
        vret = False, str(e)

    verror = vret
    if isinstance(vret, tuple):
        if len(vret) > 1:
            verror = vret[1]
        vret = vret[0]

    if vret:
        # No problems occurred, module is allowed to load
        # Return the mod's name as the defined __virtualname__ if defined,
        # else, the base_name
        return {"name": name}
    else:
        # __virtual__ explicitly disabled the loading of this module
        err = LoadError(f"Module {bname} returned virtual FALSE", verror=verror)
        # Return the load error with name as the base_name because another
        # module is still allowed to load under the same __virtualname__
        # but also return the vname information
        return {"name": base_name, "vname": name, "error": err}


def load_virtual(
    hub: "pop.hub.Hub", mod: "LoadedMod" or LoadError, bname: str
) -> dict[str, Any]:
    """
    Run the __virtual__ function to name the module and check for all loader errors
    :param hub: The redistributed pop central hub
    :param virtual: Toggle whether or not to process __virtual__ functions
    :param mod: A loader module or a LoadError if the module didn't load
    :param bname: The base name of the mod's path
    """
    return _load_virtual(hub, mod, bname, "__virtual__")


async def load_sub_virtual(
    hub: "pop.hub.Hub", mod: "LoadedMod" or LoadError, bname: str
) -> dict[str, Any]:
    """
    Run the __sub_virtual__ function to name the module and check for all loader errors
    :param hub: The redistributed pop central hub
    :param virtual: Toggle whether or not to process __virtual__ functions
    :param mod: A loader module or a LoadError if the module didn't load
    :param bname: The base name of the mod's path
    """
    _, name = _base_name(bname, mod)
    if name != "init":
        return {"name": name}
    return await _load_virtual(hub, mod, bname, "__sub_virtual__")


async def mod_init(sub: "pop.hub.Sub", mod: "LoadedMod", mod_name: str):
    """
    Process module's __init__ function if defined
    :param sub: The pop object that contains the loaded module data
    :param mod: A loader modul
    :param mod_name: The name of the module to get from the loader
    """
    if "__init__" in dir(mod):
        init = cpop.contract.Contracted(
            sub._hub,
            contracts=[],
            func=mod.__init__,
            ref=f"{sub._subname}.{mod_name}",
            name="__init__",
        )
        await init()


def sub_alias(this_sub: "pop.hub.Sub", mod: "LoadedMod", mod_name: str):
    """
    Check the sub alias settings and apply the alias names locally so they can be gathered into the higher level object on the hub
    :param this_sub: The pop object that contains the loaded module data
    :param mod: A loader module
    :param mod_name: The name of the module to get from the loader
    """
    if mod_name == "init":
        alias = getattr(mod, "__sub_alias__", None)
        if alias:
            this_sub._alias = alias


async def prep_loaded_mod(
    this_sub: "pop.hub.Sub",
    mod: "LoadedMod",
    mod_name: str,
    contracts: "List[cpop.contract.Wrapper]",
    recursive_contracts: "List[cpop.contract.Wrapper]",
) -> "LoadedMod":
    """
    Read the attributes of a python module and create a LoadedMod, which resolves
    aliases and omits objects that should not be exposed.
    :param this_sub: The pop object that contains the loaded module data
    :param mod: A loader module
    :param mod_name: The name of the module to get from the loader
    :param contracts: Contracts functions to add to the sub
    :param recursive_contracts:
    """
    ordered_contracts = contracts + recursive_contracts

    lmod = this_sub._loaded.get(mod_name, LoadedMod(mod_name))
    ref = f"{this_sub._subname}.{mod_name}"  # getattr(hub, ref) should resolve to this module

    # Recursively get the full reference to this mod
    root = this_sub._root
    while hasattr(root, "_subname"):
        ref = f"{root._subname}.{ref}"
        root = root._root

    sub_alias(this_sub, mod, mod_name)

    __func_alias__: Callable or dict[str, str or Callable] = getattr(
        mod, "__func_alias__", {}
    )
    # If __func_alias__ is a function, run it and replace the function with it's returned dictionary
    if asyncio.iscoroutinefunction(__func_alias__):
        __func_alias__ = await __func_alias__(this_sub._hub)

    # Get all the attributes from the loaded mod
    for attr in getattr(mod, "__load__", dir(mod)):
        # For an attribute in the module, get it's function alias
        func_alias: str = __func_alias__.get(attr, attr)
        func = getattr(mod, attr)
        name = func_alias
        if not this_sub._omit_vars:
            if (
                not inspect.isfunction(func)
                and not inspect.isclass(func)
                and type(func).__name__ != "cython_function_or_method"
            ):
                setattr(lmod, name, func)
                continue
        if attr.startswith(tuple(this_sub._omit_start)):
            continue
        if attr.endswith(tuple(this_sub._omit_end)):
            continue
        if (
            inspect.isfunction(func)
            or inspect.isbuiltin(func)
            or type(func).__name__ == "cython_function_or_method"
        ):
            obj = cpop.contract.create_contracted(
                this_sub._hub,
                ordered_contracts,
                func,
                ref,
                name,
            )
            if not this_sub._omit_func:
                if this_sub._pypath and not func.__module__.startswith(mod.__name__):
                    # We're only interested in functions defined in this module, not
                    # imported functions
                    continue
                lmod._funcs[name] = obj
        else:
            klass = func
            if not this_sub._omit_class and inspect.isclass(klass):
                # We're only interested in classes defined in this module, not
                # imported classes
                if not klass.__module__.startswith(mod.__name__):
                    continue
                lmod._classes[name] = klass

    # Add external aliased functions to the loaded mod
    for attr, func_alias in __func_alias__.items():
        if isinstance(func_alias, cpop.contract.Contracted):
            obj = func_alias
        elif isinstance(func_alias, Callable):
            obj = cpop.contract.create_contracted(
                this_sub._hub,
                ordered_contracts,
                func_alias,
                ref,
                attr,
                implicit_hub=False,
            )
        else:
            continue
        lmod._funcs[attr] = obj

    return lmod


class LoadedMod(types.ModuleType):
    """
    The LoadedMod class allows for the module loaded onto the sub to return
    custom sequencing, for instance it can be iterated over to return all
    functions
    """

    def __init__(self, name: str):
        super().__init__(name)
        vars = {}
        funcs = {}
        classes = {}
        self._attrs = cpop.data.MultidictCache([funcs, classes, vars])
        self._vars = vars
        self._funcs = funcs
        self._classes = classes

    def __getattr__(self, item: str):
        if item.startswith("_"):
            return self.__getattribute__(item)
        try:
            return self._attrs[item]
        except KeyError as e:
            raise AttributeError(e)

    def __getitem__(self, item: str):
        return self._attrs[item]

    def __setattr__(self, item: str, value):
        if item.startswith("_"):
            object.__setattr__(self, item, value)
        elif isinstance(value, types.FunctionType):
            self._funcs[item] = value
        elif isinstance(value, type):
            self._classes[item] = value
        else:
            self._vars[item] = value

    def __getstate__(self):
        return {
            "vars": {k: v for k, v in self._vars.items() if isinstance(v, BASE_TYPES)}
        }

    def __setstate__(self, state: dict[str, any]):
        self._vars.update(state["vars"])
