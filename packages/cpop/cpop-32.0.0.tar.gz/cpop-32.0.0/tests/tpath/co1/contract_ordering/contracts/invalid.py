"""
A contract with an invalid order value
"""


async def pre_acc(hub, ctx):
    await hub.co.PRE_ORDER.append(__name__)


__order__ = "taco"
