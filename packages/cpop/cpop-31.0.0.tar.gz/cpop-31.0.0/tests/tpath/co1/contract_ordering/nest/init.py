__contracts__ = [
    # These should be applied in the order they show up in this list
    "clash",
    "unordered_4",
    "unordered_3",
    "unordered_2",
    "unordered_1",
    "verify_pass",
    "nonexistent",
    # These contracts have the same order, so they should fall back to their order in this list
    "dup2",
    "dup1",
    # These contracts have a defined order that should override their place in this list
    "pos_first",
    "pos",
    "neg",
    "neg_last",
]


async def acc(hub) -> list:
    return []
