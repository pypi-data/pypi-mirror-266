import inspect
import sys

import cpop.contract


async def __init__(hub):
    hub.log.LOGGER = {}
    hub.log.FILE_HANDLER = None
    hub.log.STREAM_HANDLER = None
    hub.log.LEVEL = {
        "notset": hub.lib.logging.NOTSET,
        "trace": 5,
        "debug": hub.lib.logging.DEBUG,
        "info": hub.lib.logging.INFO,
        "warn": hub.lib.logging.WARN,
        "warning": hub.lib.logging.WARNING,
        "error": hub.lib.logging.ERROR,
        "fatal": hub.lib.logging.FATAL,
        "critical": hub.lib.logging.CRITICAL,
    }


def _stack_frames(relative_start: int) -> inspect.FrameInfo:
    """
    Efficiently access stack frames.
    :param relative_start: Starting stack depth; The default, 2 is the parent of the
            caller of stack_frames - the first function that may be unknown.
    :return: a stack frame
    """
    if hasattr(sys, "_getframe"):
        # implementation detail of CPython, speeds things up by 100x.
        frame = sys._getframe(relative_start)
        while frame:
            yield frame
            frame = frame.f_back
    else:
        for frame_info in inspect.stack(context=0)[relative_start:]:
            yield frame_info.frame


def _get_hub_ref():
    # Minimize lookup time by starting at frame 5, it will be at least that far back
    for frame in _stack_frames(5):
        if isinstance(frame.f_locals.get("self"), cpop.contract.Contracted):
            contracted = frame.f_locals["self"]
            return contracted, frame.f_lineno

    # Default to the root reference
    return None, 0


def _get_logger(hub, name: str = ""):
    if name not in hub.log.LOGGER:
        hub.log.LOGGER[name] = hub.lib.aiologger.Logger(name=name)
        hub.log.LOGGER[name].level = hub.log.INT_LEVEL
        if hub.log.FILE_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.FILE_HANDLER)
        if hub.log.STREAM_HANDLER:
            hub.log.LOGGER[name].handlers.append(hub.log.STREAM_HANDLER)
    return hub.log.LOGGER[name]


async def log(hub, level: int, msg: str, *args, **kwargs):
    if hub.log.INT_LEVEL > level:
        return
    contract, lineno = _get_hub_ref()

    if contract:
        caller = f"{contract.ref}.{contract.func.__name__}"
        mod = contract.func.__module__
        func = contract.func.__name__
    else:
        caller = "hub"
        mod = "hub"
        func = "hub"

    logger = _get_logger(hub, caller)
    record = hub.lib.aiologger.records.LogRecord(
        name=caller,
        pathname=mod,
        lineno=lineno,
        level=0,  # We have to overwrite this in a secure way
        msg=msg,
        args=args,
        func=func,
        **kwargs,
    )
    record.levelno = level
    if level == 5:
        record.levelname = "TRACE"
    else:
        try:
            record.levelname = hub.lib.aiologger.records.get_level_name(level)
        except ValueError:
            record.levelname = f"LEVEL {level}"

    await logger.handle(record)


async def setup(hub, conf: dict[str, any]):
    """
    Given the configuration data set up the logger.
    """
    # Set the logging level
    raw_level = conf["log_level"].strip().lower()
    hub.log.INT_LEVEL = (
        int(raw_level)
        if raw_level.isdigit()
        else hub.log.LEVEL.get(raw_level, hub.log.LEVEL["info"])
    )

    # Set up the console handler
    console_formatter = hub.lib.aiologger.formatters.base.Formatter(
        fmt=conf["log_fmt_console"], datefmt=conf["log_datefmt"]
    )
    console_handler = hub.lib.aiologger.handlers.streams.AsyncStreamHandler(
        formatter=console_formatter, stream=hub.lib.sys.stderr
    )
    console_handler.level = hub.log.INT_LEVEL
    hub.log.STREAM_HANDLER = console_handler

    # Set up the file handler
    log_file = hub.lib.pathlib.Path(conf["log_file"]).expanduser()
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_formatter = hub.lib.aiologger.formatters.base.Formatter(
        fmt=conf["log_fmt_logfile"], datefmt=conf["log_datefmt"]
    )
    file_handler = hub.lib.aiologger.handlers.files.AsyncFileHandler(log_file)
    file_handler.formatter = file_formatter
    file_handler.level = hub.log.INT_LEVEL
    hub.log.FILE_HANDLER = file_handler

    # Setup the root logger
    _get_logger(hub, name="")

    # Put all these functions higher up on the hub
    hub.log.log = hub.log["async"].log
    hub.log.trace = lambda msg, *args, **kwargs: hub.log.log(
        level=5, msg=msg, *args, **kwargs
    )
    hub.log.debug = lambda msg, *args, **kwargs: hub.log.log(
        level=hub.lib.aiologger.levels.LogLevel.DEBUG, msg=msg, *args, **kwargs
    )
    hub.log.info = lambda msg, *args, **kwargs: hub.log.log(
        level=hub.lib.aiologger.levels.LogLevel.INFO, msg=msg, *args, **kwargs
    )
    hub.log.warning = lambda msg, *args, **kwargs: hub.log.log(
        level=hub.lib.aiologger.levels.LogLevel.WARNING, msg=msg, *args, **kwargs
    )
    hub.log.error = lambda msg, *args, **kwargs: hub.log.log(
        level=hub.lib.aiologger.levels.LogLevel.ERROR, msg=msg, *args, **kwargs
    )
    hub.log.critical = lambda msg, *args, **kwargs: hub.log.log(
        level=hub.lib.aiologger.levels.LogLevel.CRITICAL, msg=msg, *args, **kwargs
    )
