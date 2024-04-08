import asyncio
import typing
from contextlib import contextmanager
from uuid import uuid4


TASK_ADDRESS_TP_TRACE_IDS: typing.Dict[int, typing.List[str]] = dict()


def _add_trace_id(task_address: int, trace_id_str: str):
    if task_address not in TASK_ADDRESS_TP_TRACE_IDS:
        TASK_ADDRESS_TP_TRACE_IDS[task_address] = [trace_id_str]
    else:
        TASK_ADDRESS_TP_TRACE_IDS[task_address].append(trace_id_str)


def _get_task_id() -> typing.Optional[int]:
    if asyncio.get_event_loop().is_running():
        task = asyncio.current_task()
        if task:
            return id(task)


def _remove_task_traces(task_address: int):
    if task_address in TASK_ADDRESS_TP_TRACE_IDS:
        del TASK_ADDRESS_TP_TRACE_IDS[task_address]


@contextmanager
def trace_id() -> typing.ContextManager[str]:
    task_address: int = _get_task_id()
    trace_id_str = uuid4().__str__()
    if task_address:
        _add_trace_id(task_address, trace_id_str)
    try:
        if task_address:
            yield trace_id_str
        else:
            yield
    finally:
        if task_address:
            TASK_ADDRESS_TP_TRACE_IDS[task_address].remove(trace_id_str)
            if not TASK_ADDRESS_TP_TRACE_IDS[task_address]:
                del TASK_ADDRESS_TP_TRACE_IDS[task_address]


def get_trace_ids() -> typing.Union[typing.List[str], None]:
    task_address = _get_task_id()
    if task_address is None:
        return
    if task_address in TASK_ADDRESS_TP_TRACE_IDS:
        return [*TASK_ADDRESS_TP_TRACE_IDS[task_address]]


def add_trace_id(
    trace_id_str: typing.Optional[typing.Union[str, typing.List[str]]] = None
) -> typing.Optional[str]:
    task_address = _get_task_id()
    if task_address is None:
        return
    if isinstance(trace_id_str, list):
        if task_address not in TASK_ADDRESS_TP_TRACE_IDS:
            TASK_ADDRESS_TP_TRACE_IDS[task_address] = [*trace_id_str]
        else:
            TASK_ADDRESS_TP_TRACE_IDS[task_address] += trace_id_str
    else:
        if trace_id_str is None:
            trace_id_str = uuid4().__str__()
        _add_trace_id(task_address, trace_id_str)
    asyncio.current_task().add_done_callback(lambda _: _remove_task_traces(task_address))
    return trace_id_str
