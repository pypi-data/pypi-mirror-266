import inspect

import cpop.data
from cpop.contract import Contracted


async def test_contracted_shortcut():
    async def f(hub):
        pass

    mock_hub = cpop.data.NamespaceDict(_tasks=[])
    c = Contracted(hub=mock_hub, contracts=[], func=f, ref="", name="")
    c.contract_functions["pre"] = [
        None
    ]  # add some garbage so we raise if we try to evaluate contracts

    await c()


async def test_contracted_inspect():
    def f(hub, p1, p2=None):
        pass

    c = Contracted(None, [], f, "", "")

    assert str(inspect.signature(c)) == str(inspect.signature(f))
    assert str(inspect.signature(c)) == "(hub, p1, p2=None)"
