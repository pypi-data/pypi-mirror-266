"""
Used to resolve resolutions to paths on the hub
"""


def last(hub: "pop.hub.Hub", ref: str) -> "pop.hub.Sub":
    """
    Takes a string that references the desired ref and returns the last object
    called out in that ref
    """
    return path(hub, ref)[-1]


def path(hub: "pop.hub.Hub", ref: str) -> list["pop.hub.Sub"]:
    """
    Retuns a list of references up to the named ref
    """
    ret = [hub]
    if isinstance(ref, str):
        ref = ref.split(".")
    for chunk in ref:
        ret.append(getattr(ret[-1], chunk))
    return ret
