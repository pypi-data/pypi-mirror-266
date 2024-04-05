"""
A contract with a negative order value that should always come last
"""

__order__ = -1


async def pre_acc(hub, ctx):
    await hub.co.PRE_ORDER.append(__name__)


async def post_acc(hub, ctx):
    ctx.ret.append(__name__)
    return ctx.ret
