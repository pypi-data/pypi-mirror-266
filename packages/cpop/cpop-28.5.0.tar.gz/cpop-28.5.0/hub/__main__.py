import asyncio
import pathlib
import pickle
from collections.abc import Callable
from collections.abc import Iterable
from pprint import pprint

import pop.contract
import pop.data
import pop.hub


def save_hub_state(hub, state_file: pathlib.Path):
    # Manually retrieve the state using __getstate__
    state = hub.__getstate__()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("wb") as f:
        pickle.dump(state, f)


def load_hub_state(hub, state_file: pathlib.Path):
    if state_file.exists():
        try:
            with state_file.open("rb") as f:
                state = pickle.load(f)
        except:
            return
        if hub._init_kwargs != state["init_kwargs"]:
            hub.__init__(**state["init_kwargs"])
        hub.__setstate__(state)
        return hub


def main():
    # Create the hub, loading all dynes and starting the loop
    hub = pop.hub.Hub(cli="pop_cli")

    original_opt = hub.OPT
    ref = original_opt.pop_cli.ref

    safe_env = {"hub": pop.data.NamespaceDict(lib=hub.lib)}

    # Try to get a saved hub
    if original_opt.pop_cli.hub_state:
        hub_state = original_opt.pop_cli.hub_state
        if hub_state.startswith('f"'):
            hub_state = eval(hub_state, safe_env)

        hub_state_file = pathlib.Path(hub_state).expanduser()
        new_hub = load_hub_state(hub, hub_state_file)
    else:
        hub_state_file = None
        new_hub = None

    # Successfully loaded a hub from a file
    if new_hub is not None:
        hub = new_hub

    args = []
    kwargs = {}

    # Override hub.OPT with the the new cli
    cli = original_opt.pop_cli.cli or ref.split(".")[0]
    if cli:
        # Pass all remaining args onto the new parser

        hub._opt = hub._sync.pop.config.load(
            cli=cli, parser_args=tuple(original_opt.pop_cli.args)
        )
    else:
        # We are using the pop cli, treat all the extra args as parameters for the called function
        PLACEHOLDER = object()
        hold = PLACEHOLDER
        for arg in original_opt.pop_cli.args:
            if hold is not PLACEHOLDER:
                key, value = parse_arg(hub, hold, arg)
                kwargs[key] = value
                hold = PLACEHOLDER
            elif "=" in arg:
                key, value = parse_arg(hub, *arg.split("=", maxsplit=1))

                kwargs[key] = value
            elif arg.startswith("--"):
                hold = arg
            else:
                args.append(arg)

    # Get the named reference from the hub
    finder = hub
    parts = ref.split(".")
    for p in parts:
        if not p:
            continue
        try:
            # Grab the next attribute in the reference
            finder = getattr(finder, p)
        except AttributeError:
            try:
                # It might be a dict-like object, try getitem
                finder = finder.__getitem__(p)
            except TypeError:
                # It might be an iterable, if the next part of the ref is a digit try to access the index
                if p.isdigit() and isinstance(finder, Iterable):
                    finder = tuple(finder).__getitem__(int(p))
                else:
                    raise

    # Call the named reference on the hub
    # This allows you to do
    # $ pop idem.init.cli
    # This way you can have multiple entrypoints, or even alias the above command to "idem"
    if asyncio.iscoroutinefunction(finder) or isinstance(
        finder, (Callable, pop.contract.Contracted)
    ):
        ret = finder(*args, **kwargs)
        while asyncio.iscoroutine(ret):
            ret = hub._synchronize(ret)
    else:
        ret = finder

    # TODO handle generator ret

    try:
        pprint(ret.__dict__)
    except:
        if ret is not None:
            pprint(ret)

    # TODO add a hub.OPT.pop_cli.dest to save the result to somewhere on the hub

    if hub_state_file:
        save_hub_state(hub, hub_state_file)


def parse_arg(hub, key: str, value: str):
    # TODO do more fancy parsing of args to allow json objects or evaluated hub references to be arguments
    key = key.replace("-", "_").lstrip("_")
    if "," in value:
        value = value.split(",")

    return key, value


if __name__ == "__main__":
    main()
