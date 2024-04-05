# cython: language_level=3

import inspect
from collections.abc import Iterable
from collections.abc import Mapping
from cpython cimport dict
from cython cimport pint
from cpython.ref cimport PyObject

cdef class ContractedContext:
    """
    Contracted function calling context
    """
    cdef:
        public object func
        public list args
        public dict[str, object] kwargs
        public str ref
        public str __name__
        public object ret
        object signature
        dict[str, object] __cache

    def __init__(
        self,
        func: object,
        args: tuple,
        kwargs: dict,
        signature: object,
        ref: str,
        name: str,
        ret=None,
        cache=None,
    ):
        if cache is None:
            cache = {}

        self.func = func
        self.args = list(args)
        self.kwargs = kwargs
        self.signature = signature
        self.ref = ref
        self.__name__ = name
        self.ret = ret
        self.__cache = cache

    @property
    def __signature__(self):
        return self.signature

    @property
    def cache(self):
        return self.__cache

    def get_arguments(self):
        """
        Return a dictionary of all arguments that will be passed to the function and their
        values, including default arguments.
        """
        if "__bound_signature__" not in self.__cache:
            self.__cache["__bound_signature__"] = self.signature.bind(
                *self.args, **self.kwargs
            )
            # Apply any default values from the signature
            self.__cache["__bound_signature__"].apply_defaults()
        return self.__cache["__bound_signature__"].arguments


def load_contract(
    contracts: "pop.hub.Sub",
    default_contracts: Iterable[str],
    mod: object,
    name: str,
) -> list[object]:
    """
    return a Contract object loaded up
    Dynamically create the correct Contracted type
    :param contracts: Contracts functions to add to the sub
    :param default_contracts: The contracts that have been marked as defaults
    :param mod: A loader module
    :param name: The name of the module to get from the loader
    """
    raws = []
    loaded_contracts = []
    if hasattr(contracts, name):
        loaded_contracts.append(name)
        raws.append(getattr(contracts, name))
    if hasattr(contracts, "init"):
        if "init" not in loaded_contracts:
            loaded_contracts.append("init")
            raws.append(getattr(contracts, "init"))
    if hasattr(mod, "__contracts__"):
        cnames = getattr(mod, "__contracts__")
        for cname in cnames:
            if cname in contracts:
                loaded_contracts.append(cname)
                raws.append(getattr(contracts, cname))
    return raws

cdef class Contracted:
    """
    This class wraps functions that have a contract associated with them
    and executes the contract routines
    """
    cdef:
        public bint _has_contracts
        public bint implicit_hub
        public dict[str, list[object]] contract_functions
        public object hub
        public object func
        public object signature
        public str __name__
        public str ref
        list _sig_errors
        list contracts
        object __wrapped__


    def __init__(self, hub, contracts:list, func:object, ref:str, name:str, implicit_hub:bool=True):
        self.__name__ = name
        self.__wrapped__ = func
        self._sig_errors = []
        self.contracts = contracts or []
        self.func = func
        self.hub = hub
        self.implicit_hub = implicit_hub
        self.ref = ref
        # Manually define the function signature if needed
        self.signature = inspect.signature(self.func)

        self._load_contracts()

    @property
    def __signature__(self):
        return self.signature

    @property
    def __dict__(self):
        return self.func.__dict__

    cdef _get_contracts_by_type(self, contract_type:str):
        matches = []
        fn_contract_name = f"{contract_type}_{self.__name__}"
        for contract in self.contracts:
            if hasattr(contract, fn_contract_name):
                matches.append(getattr(contract, fn_contract_name))
            if hasattr(contract, contract_type):
                matches.append(getattr(contract, contract_type))

        if contract_type == "post":
            matches.reverse()

        return matches

    cdef _load_contracts(self):
        # if Contracted - only allow regular pre/post
        # if ContractedAsync - allow coroutines and functions

        self.contract_functions = {
            "pre": self._get_contracts_by_type("pre"),
            "call": self._get_contracts_by_type("call")[:1],
            "post": self._get_contracts_by_type("post"),
        }
        self._has_contracts = sum(len(l) for l in self.contract_functions.values()) > 0

    async def __call__(self, *args, **kwargs):
        if self.implicit_hub:
            args = (self.hub,) + args

        if not self._has_contracts:
            ret = await self.func(*args, **kwargs)
            return ret
        contract_context = ContractedContext(
            self.func, args, kwargs, self.signature, self.ref, self.__name__
        )

        # Process pre contracts
        for fn in self.contract_functions["pre"]:
            pre_ret = await fn(contract_context)

            await self.hub.pop.contract.process_pre_result(pre_ret, fn, self)

        # Call the one call contract
        if self.contract_functions["call"]:
            ret = await self.contract_functions["call"][0](contract_context)
        else:
            ret = await self.func(*contract_context.args, **contract_context.kwargs)

        # Handle post contracts
        for fn in self.contract_functions["post"]:
            contract_context.ret = ret
            post_ret = await fn(contract_context)
            if post_ret is not None:
                ret = post_ret

        return ret

    def __getstate__(self):
        return {
            "ref": self.ref,
            "name": self.__name__,
            "implicit_hub": self.implicit_hub,
            "contracts": self.contracts,
        }

    def __setstate__(self, state:dict[str, object]):
        self.ref = state["ref"]
        self.__name__ = state["name"]
        self.func = self.hub[self.ref][self.__name__].func
        self.implicit_hub = state["implicit_hub"]
        self.contracts = state["contracts"]



class ContractedAsyncGen(Contracted):
    async def __call__(self, *args, **kwargs):
        if self.implicit_hub:
            args = (self.hub,) + args

        if not self._has_contracts:
            async for chunk in self.func(*args, **kwargs):
                yield chunk
            return
        contract_context = ContractedContext(
            self.func, args, kwargs, self.signature, self.ref, self.__name__
        )

        for fn in self.contract_functions["pre"]:
            pre_ret = await fn(contract_context)

            await self.hub.pop.contract.process_pre_result(pre_ret, fn, self)
        chunk = None
        if self.contract_functions["call"]:
            async for chunk in self.contract_functions["call"][0](contract_context):
                yield chunk
        else:
            async for chunk in self.func(
                *contract_context.args, **contract_context.kwargs
            ):
                yield chunk
        ret = chunk
        for fn in self.contract_functions["post"]:
            contract_context.ret = ret
            post_ret = await fn(contract_context)
            if post_ret is not None:
                ret = post_ret

def create_contracted(
    hub: "pop.hub.Hub",
    contracts: list["pop.loader.LoadedMod"],
    func: functools.partial,
    ref: str,
    name: str,
    implicit_hub: bool = True,
) -> Contracted:
    """
    Dynamically create the correct Contracted type
    :param hub: The redistributed pop central hub
    :param contracts: Contracts functions to add to the sub
    :param func: The contracted function to call
    :param ref: The reference to the function on the hub
    :param name: The name of the module to get from the loader
    :param implicit_hub: True if a hub should be implicitly injected into the "call" method
    """
    if inspect.isasyncgenfunction(func):
        return ContractedAsyncGen(hub, contracts, func, ref, name, implicit_hub)
    else:
        return Contracted(hub, contracts, func, ref, name, implicit_hub)
