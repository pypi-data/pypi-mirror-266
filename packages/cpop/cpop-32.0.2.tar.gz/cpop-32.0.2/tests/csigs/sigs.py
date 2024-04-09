async def first(hub, a, b, c: str, **kwargs):
    return a * b * c


async def second(hub, a, b=7, **kwargs):
    pass


async def third(hub, a, b, c, d=3):
    pass


async def four(hub, a, b, c, d, *args, e=4):
    pass


async def five(hub, a: str, d, *args):
    pass


async def six(hub, *args):
    pass


async def seven(hub, foo, bar):
    pass
