async def param_alias_tuple(hub, id_: (str, "alias=id")):
    return id_


async def param_alias_str(hub, id_: "alias=id"):
    return id_


async def param_alias_mult(hub, id_: ("alias=id", "alias=taco")):
    return id_
