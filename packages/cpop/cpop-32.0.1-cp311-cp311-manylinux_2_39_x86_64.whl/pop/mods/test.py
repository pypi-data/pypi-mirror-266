async def func(hub, *args, **kwargs):
    return args, kwargs


async def benchmark(hub, depth=5, width=10000):
    """
    Create a bloated hub

    Run a pop with all the strict contract checking

    .. code-block:: bash

        python -m hub pop.test.benchmark

    Run an optimized pop

    .. code-block:: bash

        python -O -m hub pop.test.benchmark
    """
    await hub.log.debug("Started Benchmark")
    start_time = hub.lib.time.time()
    for w in range(int(width)):
        name = f"sub_{w}"
        await hub.pop.sub.add(dyne_name=name)
        dyne = hub[name]
        for d in range(int(depth)):
            nest_name = f"sub_{d}_{d}"
            await hub.pop.sub.add(dyne_name=nest_name, sub=dyne)
            dyne = dyne[nest_name]
    end_time = hub.lib.time.time()
    return f"Total time taken: {end_time - start_time:.2f} seconds."
