import asyncio
import importlib.machinery
import os
import secrets
import signal
import sys
from collections.abc import Iterable
from types import ModuleType
from typing import Any

import cpop.contract
import cpop.data
import pop.dirs
import pop.exc
import pop.loader
import pop.ref
import pop.scanner
import pop.verify

try:
    pass

    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False


def ex_path(path: str) -> list[str]:
    """
    Take a path that is sent to the Sub and expand it if it is a string or not
    """
    if isinstance(path, str):
        return path.split(",")
    elif isinstance(path, list):
        return path
    else:
        return []


class PopMeta(cpop.data.MultidictCache):
    def __init__(self, data: list[dict[str, any]]):
        attrs = {}
        data.append(attrs)
        super().__init__(data)
        object.__setattr__(self, "_attrs", attrs)

    def __setitem__(self, key: str, value):
        # Recurse the dotted reference and set the value on the last part of the reference
        if "." in key:
            parts = key.split(".")
            finder = self
            for p in parts[:-1]:
                if not p:
                    continue
                if p not in finder:
                    finder[p] = cpop.data.NamespaceDict()
                finder = finder[p]

            finder[parts[-1]] = value
        else:
            self._attrs[key] = value

    def __setattr__(self, key: str, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            self[key] = value


class Hub(PopMeta):
    """
    The redistributed pop central hub. All components of the system are
    rooted to the Hub.
    """

    def __init__(self, *args, **kwargs):
        subs = {}
        sub_alias = {}
        imports = {}
        PopMeta.__init__(self, [subs, sub_alias, imports])
        self._subs = subs
        self._sub_alias = sub_alias
        self._imports = imports
        self._dynamic = None
        self._dscan = False
        # Set up the conf OPT structure so it is always available
        self._opt = None
        self._task_count = 0
        self._aio_alive = {}

    async def __ainit__(
        self,
        load_all_dynes: bool = True,
        load_all_subdirs: bool = True,
        recurse_subdirs: bool = True,
        pop_mods: list[str] = None,
        cli: str = None,
        logs: bool = True,
        load_config: bool = True,
    ):
        self._init_kwargs = {
            k: v for k, v in locals().items() if k != "self" and not k.startswith("_")
        }
        self._tasks = asyncio.Queue()

        # Add the dyne for python imports to live in to the hub
        if "lib" not in self._subs:
            self._subs["lib"] = await AsyncSub(
                self, subname="lib", dyne_name="lib", pypath=pop_mods
            )
            # Load all existing libraries onto hub.lib
            self._subs["lib"]._imports.update(
                {
                    base: mod
                    for base, mod in sys.modules.items()
                    if not base.startswith("_") and "." not in base
                }
            )

        if "pop" not in self._subs:
            if pop_mods is None:
                pop_mods = ["pop.mods"]

            # Add the pop sub to the hub, this should always use pypath and
            # Should never be made dynamic. This is a core system sub and should
            # NOT be app-merged
            self._subs["pop"] = await AsyncSub(self, subname="pop", pypath=pop_mods)
            await self._subs["pop"]._load_all()

        self._load_all_dynes = load_all_dynes
        self._load_all_subdirs = load_all_subdirs
        self._recurse_subdirs = recurse_subdirs
        if self._load_all_dynes:
            self._scan_dynamic()
            await self._load_all()

            if load_config:
                # Overwrite opt with config data
                self._opt = await self.pop.config.load(cli=cli, **self._dynamic.config)

        # Set up a logger
        if "log" in self._subs and logs:
            await self.log[self._opt.log.log_plugin].setup(self._opt.log.copy())

    @property
    def OPT(self):
        return self._opt

    async def _load_all(self):
        for base, imp in self._dynamic.imports.items():
            self._subs["lib"]._imports[base] = imp

        # Load all dynamic subs onto the hub
        for dyne in self._dynamic.dyne:
            if dyne in self._subs:
                continue
            await self.pop.sub.add(dyne_name=dyne)
            if not self._load_all_subdirs:
                continue
            await self.pop.sub.load_subdirs(
                self._subs[dyne], recurse=self._recurse_subdirs
            )

    def _loop_start(self, *coros, holder=True, sigint=None, sigterm=None):
        """
        Start a loop with a holder coroutine to run a long running application with background task tracking
        """
        loop = asyncio.get_running_loop()
        if sigint:
            s = signal.SIGINT
            loop.add_signal_handler(s, lambda s=s: loop.create_task(sigint(s)))
        if sigterm:
            s = signal.SIGTERM
            loop.add_signal_handler(s, lambda s=s: loop.create_task(sigterm(s)))
        if holder:
            coros = list(coros)
            coros.append(self._holder())

        try:
            # DO NOT CHANGE THIS CALL TO run_forever! If we do that then the tracebacks
            # do not get resolved.
            return loop.run_until_complete(asyncio.gather(*coros))
        except KeyboardInterrupt:
            print("Caught keyboard interrupt. Canceling...")
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    async def _holder(self):
        """
        Just a sleeping while loop to hold the loop open while it runs until
        complete
        """
        while True:
            complete = await self._tasks.get()
            await complete["task"]
            if complete["cb"]:
                await self._auto(complete["cb"])
            self._task_count -= 1
            if self.task_count == 0:
                break

    def _auto(hub, coro, cb_coro=None):
        """
        Start a task that will be automatically awaited

        coro: An unscheduled coroutine object to run
        cb_coro: An unscheduled coroutine to run when the main coroutine completes
        """
        hub._task_count += 1

        task = hub.lib.asyncio.create_task(coro)

        def _callback(task):
            hub._tasks.put_nowait({"task": task, "cb": cb_coro})

        task.add_done_callback(_callback)
        return task

    def __getstate__(self) -> dict:
        attrs = {}
        for k, v in self._attrs.items():
            if isinstance(v, pop.loader.BASE_TYPES):
                attrs[k] = v
            elif isinstance(v, dict):
                if all(isinstance(v2, pop.loader.BASE_TYPES) for v2 in v.values()):
                    attrs[k] = v
            elif isinstance(v, Iterable):
                if all(isinstance(v2, pop.loader.BASE_TYPES) for v2 in v):
                    attrs[k] = v
        state = dict(
            init_kwargs=self._init_kwargs,
            subs={name: sub.__getstate__() for name, sub in self._subs.items()},
            aliases=self._sub_alias,
            OPT=cpop.data.unfreeze(self._opt),
            imports={subname: mod.__name__ for subname, mod in self._imports.items()},
            attrs=attrs,
        )
        return state

    def __setstate__(self, state: dict):
        subs = state["subs"]
        opt = state["OPT"]
        aliases = state["aliases"]

        for subname, modname in state["imports"].items():
            try:
                self._imports[subname] = importlib.import_module(modname)
            except ModuleNotFoundError:
                ...
        self._attrs.update(state["attrs"])
        self._sub_alias.update(aliases)
        self._opt = cpop.data.freeze(opt)

        # Schedule the hub's async init function to run later
        self._auto(self.__ainit__())
        for name, data in subs.items():
            if name in self._subs:
                sub = self._subs[name]
            else:
                sub = Sub(hub=self, root=self, **data["init_kwargs"])
                self._subs[name] = sub

            sub.__setstate__(data)

    def _scan_dynamic(self):
        """
        Refresh the dynamic roots data used for loading app merge module roots
        """
        self._clear()
        self._dynamic = pop.dirs.dynamic_dirs()
        self._dscan = True

    def __getattr__(self, item: str):
        if item.startswith("_"):
            return self.__getattribute__(item)
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"Hub has no attribute '{item}'")


class Sub(PopMeta):
    """
    The pop object that contains the loaded module data
    """

    def __init__(
        self,
        hub: Hub,
        *,
        subname: str,
        root: PopMeta = None,
        pypath: list[str] = None,
        static: list[str] = None,
        contracts_pypath: list[str] = None,
        contracts_static: list[str] = None,
        default_contracts: list[str] = None,
        virtual: bool = True,
        dyne_name: str = None,
        omit_start: tuple[str] = ("_",),
        omit_end: tuple[str] = (),
        omit_func: bool = False,
        omit_class: bool = False,
        omit_vars: bool = False,
        mod_basename: str = "",
        stop_on_failures: bool = False,
        init: bool = True,
        is_contract: bool = False,
        sub_virtual: bool = True,
        recursive_contracts_static: list[str] = None,
        default_recursive_contracts: list[str] = None,
    ):
        """
        :param hub: The redistributed pop central hub
        :param subname: The name that the sub is going to take on the hub
            if nothing else is passed, it is used as the pypath
        :param pypath: One or many python paths which will be imported
        :param static: Directories that can be explicitly passed
        :param contracts_pypath: Load additional contract paths
        :param contracts_static: Load additional contract paths from a specific directory
        :param default_contracts: Specifies that a specific contract plugin will be applied as a default to all plugins
        :param virtual: Toggle whether or not to process __virtual__ functions
        :param dyne_name: The dynamic name to use to look up paths to find plugins -- linked to conf.py
        :param omit_start: Allows you to pass in a tuple of characters that would omit the loading of any object
            I.E. Any function starting with an underscore will not be loaded onto a plugin
            (You should probably never change this)
        :param omit_end:Allows you to pass in a tuple of characters that would omit the loading of an object
            (You should probably never change this)
        :param omit_func: bool: Don't load any functions
        :param omit_class: bool: Don't load any classes
        :param omit_vars: bool: Don't load any vars
        :param mod_basename: str: Manipulate the location in sys.modules that the plugin will be loaded to.
            Allow plugins to be loaded into a separate namespace.
        :param stop_on_failures: If any module fails to load for any reason, stacktrace and do not continue loading this sub
        :param init: bool: determine whether or not we process __init__ functions
        :param is_contract: Specify whether or not this sub is a contract
        :param sub_virtual: bool: Recursively ignore this sub and it's subs
        """
        self._init_kwargs = {
            k: v
            for k, v in locals().items()
            if k not in ("self", "hub", "root") and not k.startswith("_")
        }
        subs = {}
        sub_alias = {}
        imports = {}
        loaded = {}
        # tracks what has been setattr-ed on this sub for performance; if something needs to be
        # *removed*, we can delattr everything in _cached, it will be re-set on the next call.
        super().__init__([loaded, subs, sub_alias, imports])
        self._subs = subs
        self._sub_alias = sub_alias
        self._imports = imports
        self._loaded = loaded
        self._reload_mods = {}
        self._alias = []
        self._loaded_all = False
        self._load_errors = {}
        self._vmap = {}
        self._hub = hub
        self._root = root or hub
        self._subname = subname
        self._pypath = ex_path(pypath)
        self._static = ex_path(static)
        self._contracts_pypath = ex_path(contracts_pypath)
        self._contracts_static = ex_path(contracts_static)
        self._recursive_contracts_static = ex_path(recursive_contracts_static)
        self._default_recursive_contracts = default_recursive_contracts or []
        self._default_contracts = default_contracts or ()
        self._dyne_name = dyne_name
        self._virtual = virtual
        self._omit_start = omit_start
        self._sub_virtual = sub_virtual
        self._omit_end = omit_end
        self._omit_func = omit_func
        self._omit_class = omit_class
        self._omit_vars = omit_vars
        self._mod_basename = mod_basename
        self._stop_on_failures = stop_on_failures
        self._is_contract = is_contract
        self._process_init = init

    async def __ainit__(self, *args, **kwargs):
        await self._prepare()

    async def _prepare(self):
        self._dirs = pop.dirs.dir_list(
            self._pypath,
            self._static,
        )

        if self._dyne_name:
            self._load_dyne()
        self._contract_dirs = pop.dirs.dir_list(
            self._contracts_pypath,
            self._contracts_static,
        )
        self._contract_dirs.extend(pop.dirs.inline_dirs(self._dirs, "contracts"))
        self._recursive_contract_dirs = pop.dirs.dir_list(
            [],
            self._recursive_contracts_static,
        )
        self._recursive_contract_dirs.extend(
            pop.dirs.inline_dirs(self._dirs, "recursive_contracts")
        )

        self._contract_subs = []
        for i in range(len(self._contract_dirs)):
            sub = await AsyncSub(
                hub=self._hub,
                subname=f"{self._subname}._contract_subs[{i}]",
                static=[self._contract_dirs[i]],
                is_contract=True,
            )
            await sub._load_all()
            self._contract_subs.append(sub)

        self._recursive_contract_subs = []
        if self._recursive_contract_dirs:
            self._recursive_contract_dirs += getattr(
                self._root, "_recursive_contract_dirs", []
            )
            # child Subs look at the parent's _recursive_contract_dirs, so we can't modify it
            filtered_recursive_contract_dirs = sorted(
                set(self._recursive_contract_dirs) - set(self._contract_dirs)
            )
            for i in range(len(filtered_recursive_contract_dirs)):
                sub = await AsyncSub(
                    hub=self._hub,
                    subname=f"{self._subname}._recursive_contract_subs[{i}]",
                    static=[filtered_recursive_contract_dirs[i]],
                    is_contract=True,
                )
                await sub._load_all()
                self._recursive_contract_subs.append(sub)
        else:
            # copy parent's recursive contracts
            self._recursive_contract_dirs = getattr(
                self._root, "_recursive_contract_dirs", []
            )
            self._recursive_contract_subs = getattr(
                self._root, "_recursive_contract_subs", []
            )

        self._name_root = self._load_name_root()
        self._scan = pop.scanner.scan(self._dirs)

    def _load_dyne(self):
        """
        Load up the dynamic dirs for this sub
        """
        if not self._hub._dscan:
            self._hub._scan_dynamic()
        for path in self._hub._dynamic.dyne.get(self._dyne_name, {}).get("paths", []):
            if path not in self._dirs:
                self._dirs.append(path)

        self._clear()

    def _load_name_root(self):
        """
        Generate the root of the name to be used to apply to the loaded modules
        """
        if self._pypath:
            return self._pypath[0]
        elif self._dirs:
            return secrets.token_hex()

    def __getstate__(self):
        attrs = {}
        for k, v in self._attrs.items():
            if isinstance(v, pop.loader.BASE_TYPES):
                attrs[k] = v
            elif isinstance(v, dict):
                if all(isinstance(v2, pop.loader.BASE_TYPES) for v2 in v.values()):
                    attrs[k] = v
            elif isinstance(v, Iterable):
                if all(isinstance(v2, pop.loader.BASE_TYPES) for v2 in v):
                    attrs[k] = v
        return dict(
            init_kwargs=self._init_kwargs,
            loaded={
                item: dict(
                    iface=iface, bname=bname, state=self._loaded[item].__getstate__()
                )
                for item, (iface, bname) in self._reload_mods.items()
            },
            subs={name: sub.__getstate__() for name, sub in self._subs.items()},
            aliases=self._sub_alias,
            imports={subname: mod.__name__ for subname, mod in self._imports.items()},
            attrs=attrs,
        )

    def __setstate__(self, state: dict):
        """
        Only a hub can truly restore a sub because of their interdependency
        """
        subs = state["subs"]
        aliases = state["aliases"]
        imports = state["imports"]
        loaded = state["loaded"]

        self._sub_alias.update(aliases)
        # self._attrs.update(state["attrs"])

        for subname, modname in imports.items():
            try:
                self._imports[subname] = importlib.import_module(modname)
            except ModuleNotFoundError:
                ...

        for name, data in subs.items():
            sub = Sub(hub=self._hub, root=self, **data["init_kwargs"])
            sub.__setstate__(data)
            self._subs[name] = sub

        # Initialize the Sub, put these functions on the hub to be gathered
        self._hub._auto(self.__ainit__())
        self._hub._auto(self._load_all())

        # Make sure all unique items make it back onto the loaded mod
        for item, data in loaded.items():
            try:
                self._loaded[item].__setstate__(data["state"])
            except KeyError:
                ...

    def __getattr__(self, item: str):
        """
        If the item should be loaded, load it, else serve it
        """
        if item.startswith("_"):
            return self.__getattribute__(item)
        elif "." in item:
            return pop.ref.last(self._hub, item)

        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"'{self._subname}' has no attribute '{item}'")

    async def _sub_init(self):
        """
        Run load init.py for the sub, running '__init__' function if present
        """
        await self._find_mod("init", match_only=True)

    def _process_load_error(
        self, mod: ModuleType, skip_full_stop: bool = False
    ) -> bool:
        if not isinstance(mod, pop.loader.LoadError):
            # This is not a LoadError, return now!
            return False

        if mod.edict["verror"]:
            return False

        return True

    async def _find_mod(self, item: str, match_only: bool = False) -> dict:
        """
        Find the module named item
        :param item: The module to search for (then load) from any scanned interface
        :param match_only: return the loaded module
        :return a loaded mod_dict
        """
        for iface in self._scan:
            for bname in self._scan[iface]:
                if os.path.basename(bname) == item:
                    await self._load_item(iface, bname)
            if item in self._loaded:
                self._reload_mods[item] = (iface, bname)
                return self._loaded[item]
        if not match_only:
            for iface in self._scan:
                for bname in self._scan[iface]:
                    if self._scan[iface][bname].get("loaded"):
                        continue
                    await self._load_item(iface, bname)
                    if item in self._loaded:
                        self._reload_mods[item] = (iface, bname)
                        return self._loaded[item]
        # Let's see if the module being lookup is in the load errors dictionary
        if item in self._load_errors:
            # Return the LoadError
            return self._load_errors[item]

    async def _load_item(self, iface: str, bname: str):
        """
        Load the named basename
        :param iface: A scanned directory type
        :param bname: The base name of the python path of a module
        """
        # The mname is the name to give the module in python's sys.modules
        # This name must be unique for every loaded module, so we use the full
        # module path sans the file extention
        mname = self._scan[iface][bname]["path"].replace(os.sep, ".")
        mname = mname[mname.index(".") + 1 : mname.rindex(".")].strip(".")
        mod = pop.loader.load_mod(
            mname,
            iface,
            self._scan[iface][bname]["path"],
        )
        await self._prep_mod(mod, iface, bname)

    def _process_vret(self, vret: dict[str, Any]) -> bool:
        """
        :param vret: The return from a __virtual__ or __sub_virtual__ function
        :return: True if there was an error, else false
        """
        if "error" in vret:
            # Virtual Errors should not full stop pop
            self._process_load_error(vret["error"], skip_full_stop=True)
            # Store the LoadError under the __virtualname__ if defined
            self._load_errors[vret["vname"]] = vret["error"]
            return True
        else:
            return False

    async def _prep_mod(self, mod: ModuleType, iface: str, bname: str):
        """
        Prepare the module!
        :param mod: A python module containing data
        :param iface: A scanned directory type
        :param bname: The base name of the python path of a module
        """
        if not self._sub_virtual:
            return
        else:
            vret = await pop.loader.load_sub_virtual(self._hub, mod, bname)
            if self._process_vret(vret):
                self._sub_virtual = False
                return

        vret = await pop.loader.load_virtual(self._hub, mod, bname)

        if self._process_vret(vret):
            return

        contracts = []
        for contract_sub in self._contract_subs:
            contracts.extend(
                cpop.contract.load_contract(
                    contract_sub, self._default_contracts, mod, vret["name"]
                )
            )
        recursive_contracts = []
        for recursive_contract_sub in self._recursive_contract_subs:
            recursive_contracts.extend(
                cpop.contract.load_contract(
                    recursive_contract_sub,
                    self._default_recursive_contracts,
                    mod,
                    vret["name"],
                )
            )
        name = vret["name"]
        mod_dict = await pop.loader.prep_loaded_mod(
            self, mod, name, contracts, recursive_contracts
        )
        if name != "init":
            pop.verify.contract(contracts + recursive_contracts, mod_dict)
        self._loaded[name] = mod_dict
        self._vmap[mod.__file__] = name
        # Let's mark the module as loaded
        self._scan[iface][bname]["loaded"] = True
        if self._process_init:
            # Now that the module has been added to the sub, call mod_init
            await pop.loader.mod_init(self, mod, name)

    async def _load_all(self):
        """
        Load all modules found during the scan.

        .. attention:: This completely disables the lazy loader behavior of pop
        """
        if self._loaded_all is True:
            return
        for iface in self._scan:
            for bname in self._scan[iface]:
                if self._scan[iface][bname].get("loaded"):
                    continue
                await self._load_item(iface, bname)
        self._loaded_all = True


class AsyncInitWrapper:
    def __init__(self, cls):
        self.cls = cls

    async def __call__(self, *args, **kwargs):
        instance = self.cls(*args, **kwargs)
        await instance.__ainit__(*args, **kwargs)
        return instance


AsyncHub = AsyncInitWrapper(Hub)
AsyncSub = AsyncInitWrapper(Sub)
