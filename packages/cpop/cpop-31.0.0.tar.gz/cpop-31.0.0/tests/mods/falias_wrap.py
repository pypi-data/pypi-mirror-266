import pytest
from tests.external_module.api import OtherService  # noreorder


SERVICE = OtherService()


async def _wrap_service_get_method(hub, target):
    """
    `target` is used to find a method name of OtherService called `get_{target}`.

    Return the alias we should use in this plugin, as well as function that
    calls this method of OtherService.
    """
    method_name = f"get_{target}"

    def wrapper(arg1):
        method = getattr(hub._.SERVICE, target)
        return method(arg1)

    return method_name, wrapper


async def __func_alias__(hub):
    out = {"start": SERVICE.start}

    for target in "job_id", "process_id", "user_id", "parent_id":
        func_name, func = await _wrap_service_get_method(hub, target)
        out[func_name] = func

    return out


async def do_things_with_our_example(hub):
    def _try_call():
        get_job_id("super-task")

    assert pytest.raises(NameError, _try_call)

    assert await hub._.get_job_id("super-task")
    assert await hub._.get_job_id("super-task")
    assert await hub._.get_process_id("super-task")
    assert await hub._.get_user_id("super-task")
