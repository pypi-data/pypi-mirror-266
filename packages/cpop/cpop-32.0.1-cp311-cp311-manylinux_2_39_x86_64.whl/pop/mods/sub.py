"""
Control and add subsystems to the running daemon hub
"""

import pop.hub


async def add(
    hub: "pop.hub.Hub",
    dyne_name: str = None,
    *,
    pypath: list[str] = None,
    subname: str = None,
    sub: "pop.hub.Sub" = None,
    static: list[str] = None,
    contracts_pypath: list[str] = None,
    contracts_static: list[str] = None,
    default_contracts: list[str] = None,
    virtual: bool = True,
    omit_start: tuple[str] = ("_",),
    omit_end: tuple[str] = (),
    omit_func: bool = False,
    omit_class: bool = False,
    omit_vars: bool = False,
    mod_basename: str = "pop.sub",
    stop_on_failures: bool = False,
    init: bool = True,
    recursive_contracts_static: list[str] = None,
    default_recursive_contracts: list[str] = None,
    python_import: str = None,
):
    """
    Add a new subsystem to the hub
    :param hub: The redistributed pop central hub
    :param subname: The name that the sub is going to take on the hub
        if nothing else is passed, it is used as the dyne_name
    :param sub: The sub to use as the root to add to
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
    :param recursive_contracts_static: Load additional recursive contract paths from a specific directory
    :param default_recursive_contracts: Specifies that a specific recursive contract plugin will be applied as a default to all plugins
    :param python_import: Load a module from python onto the sub
    """
    if python_import:
        subname = subname if subname else python_import.split(".")[0]
    if pypath:
        pypath = pop.hub.ex_path(pypath)
        subname = subname if subname else pypath[0].split(".")[-1]
    elif static:
        subname = subname if subname else hub.lib.os.path.basename(static)
    if dyne_name:
        subname = subname if subname else dyne_name
    root = sub or hub
    # The dynamic namespace is already on the hub
    if dyne_name in root._subs:
        return

    if python_import:
        root._imports[subname] = hub.lib.importlib.import_module(python_import)
        return

    root._clear()
    root._subs[subname] = await pop.hub.AsyncSub(
        hub,
        subname=subname,
        root=root,
        pypath=pypath,
        static=static,
        contracts_pypath=contracts_pypath,
        contracts_static=contracts_static,
        default_contracts=default_contracts,
        virtual=virtual,
        dyne_name=dyne_name,
        omit_start=omit_start,
        omit_end=omit_end,
        omit_func=omit_func,
        omit_class=omit_class,
        omit_vars=omit_vars,
        mod_basename=mod_basename,
        stop_on_failures=stop_on_failures,
        init=init,
        sub_virtual=getattr(root, "_subvirt", True),
        recursive_contracts_static=recursive_contracts_static,
        default_recursive_contracts=default_recursive_contracts,
    )
    # init the sub (init.py:__init__) after it can be referenced on the hub!
    await root._subs[subname]._sub_init()
    await root._subs[subname]._load_all()
    for alias in root._subs[subname]._alias:
        root._sub_alias[alias] = root._subs[subname]


async def get_dirs(hub: "pop.hub.Hub", sub: "pop.hub.Sub") -> list[str]:
    """
    Return a list of directories that contain the modules for this subname
    :param hub: The redistributed pop central hub
    :param sub: The pop object that contains the loaded module data
    """
    return sub._dirs


async def load_subdirs(hub: "pop.hub.Hub", sub: "pop.hub.Sub", recurse: bool = False):
    """
    Given a sub, load all subdirectories found under the sub into a lower namespace
    :param hub: The redistributed pop central hub
    :param sub: The pop object that contains the loaded module data
    :param recurse: Recursively iterate over nested subs
    """
    if not sub._sub_virtual:
        return
    dirs = await hub.pop.sub.get_dirs(sub)
    roots = {}
    for dir_ in dirs:
        for fn in hub.lib.os.listdir(dir_):
            if fn.startswith("_"):
                continue
            if fn == "contracts":
                continue
            if fn == "recursive_contracts":
                continue
            full = hub.lib.os.path.join(dir_, fn)
            if not hub.lib.os.path.isdir(full):
                continue
            if fn not in roots:
                roots[fn] = [full]
            else:
                roots[fn].append(full)
    for name, sub_dirs in roots.items():
        if name.startswith("."):
            continue
        # Load er up!
        await hub.pop.sub.add(
            subname=name,
            sub=sub,
            static=sub_dirs,
            virtual=sub._virtual,
            omit_start=sub._omit_start,
            omit_end=sub._omit_end,
            omit_func=sub._omit_func,
            omit_class=sub._omit_class,
            omit_vars=sub._omit_vars,
            mod_basename=sub._mod_basename,
            stop_on_failures=sub._stop_on_failures,
        )
        if recurse:
            if isinstance(getattr(sub, name), pop.hub.Sub):
                await hub.pop.sub.load_subdirs(getattr(sub, name), recurse)


async def reload(hub: "pop.hub.Hub", subname: str):
    """
    Instruct the hub to reload the modules for the given sub. This does not call
    the init.new function or remove sub level variables. But it does re-read the
    directory list and re-initialize the loader causing all modules to be re-evaluated
    when started.
    :param hub: The redistributed pop central hub
    :param subname: The name that the sub is going to take on the hub
        if nothing else is passed, it is used as the pypath
    """
    if hasattr(hub, subname):
        sub = getattr(hub, subname)
        sub._prepare()
        return True
    else:
        return False
