"""
A contract that passes its __verify_order__ check
"""


async def pre_acc(hub, ctx):
    await hub.co.PRE_ORDER.append(__name__)


async def post_acc(hub, ctx):
    ctx.ret.append(__name__)
    return ctx.ret
