import asyncio
from collections.abc import Callable
from collections.abc import Iterable

import pop.hub

try:
    import uvloop

    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False


def save_hub_state(hub, state_file):
    # Manually retrieve the state using __getstate__
    state = hub.__getstate__()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with state_file.open("wb") as f:
        hub.lib.pickle.dump(state, f)


async def load_hub_state(hub, state_file, cli: str):
    if state_file.exists():
        try:
            async with hub.lib.aiofiles.open(state_file, "rb") as f:
                state = hub.lib.pickle.loads(await f.read())
        except:
            return

        if not state:
            return

        if hub._init_kwargs != state["init_kwargs"]:
            cli = state["init_kwargs"].pop("cli", cli)
            state["init_kwargs"].pop("load_config", None)
            await hub.__ainit__(cli=cli, **state["init_kwargs"], load_config=False)


def main():
    # Initialize the event loop
    if HAS_UVLOOP:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    asyncio.run(amain())


async def amain():
    hub = await pop.hub.AsyncHub(cli="pop_cli")

    original_opt = hub.OPT
    ref = original_opt.pop_cli.ref
    cli = original_opt.pop_cli.cli or ref.split(".")[0]

    # Try to get a saved hub
    if original_opt.pop_cli.hub_state:
        hub_state = original_opt.pop_cli.hub_state

        # Evaluate a reference the hub as the hub_state
        if hub_state.startswith('f"'):
            safe_env = {"hub": hub.lib.cpop.data.NamespaceDict(lib=hub.lib)}
            hub_state = eval(hub_state, safe_env)

        hub_state_file = hub.lib.pathlib.Path(hub_state).expanduser()
        await load_hub_state(hub, hub_state_file, cli)
    else:
        hub_state_file = None

    args = []
    kwargs = {}

    # Override hub.OPT with the the new cli
    cli = original_opt.pop_cli.cli or ref.split(".")[0]
    if cli:
        # Pass all remaining args onto the new parser

        hub._opt = await hub.pop.config.load(
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
        finder, (Callable, hub.lib.cpop.contract.Contracted)
    ):
        ret = finder(*args, **kwargs)
        if asyncio.iscoroutine(ret):
            ret = await ret
    else:
        ret = finder

    # TODO handle generator ret

    try:
        hub.lib.pprint.pprint(ret.__dict__)
    except:
        if ret is not None:
            hub.lib.pprint.pprint(ret)

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
