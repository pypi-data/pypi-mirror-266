async def sig_first(hub, a: str, b, c: list):
    pass


async def sig_second(hub, **kwargs):
    pass


async def sig_third(hub, a, b, *args, **kwargs):
    pass


async def sig_four(hub, a, *args, e=7):
    pass


async def sig_five(hub, a: str, *args):
    pass


async def sig_six(hub, a, *args, **kwargs):
    pass


async def sig_seven(hub, foo):
    pass


async def sig_missing():
    """
    This function is missing in the module to make sure it gets picked up
    """
