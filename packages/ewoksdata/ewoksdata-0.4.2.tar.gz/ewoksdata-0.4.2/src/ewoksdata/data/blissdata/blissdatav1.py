from numbers import Number
from collections import Counter
from typing import List, Optional

from numpy.typing import ArrayLike

from .exceptions import VersionError

try:
    from blissdata.beacon.data import BeaconData
    from blissdata.redis_engine.store import DataStore
    from blissdata.redis_engine.scan import Scan
    from blissdata.redis_engine.scan import ScanState
    from blissdata.redis_engine.stream import StreamingClient
    from blissdata.redis_engine.exceptions import EndOfStream
    from blissdata.redis_engine.exceptions import IndexNoMoreThereError
    from blissdata.lima.client import lima_client_factory
except ImportError as e:
    raise VersionError(str(e)) from e


def iter_bliss_scan_data_from_memory(
    db_name: str,
    lima_names: List[str],
    counter_names: List[str],
    retry_timeout: Optional[Number] = None,
    retry_period: Optional[Number] = None,
):
    data_store = _get_data_store()
    scan = data_store.load_scan(db_name, scan_cls=Scan)
    buffers = {name: list() for name in lima_names + counter_names}

    while scan.state < ScanState.PREPARED:
        scan.update()

    lima_streams = dict()
    lima_clients = dict()
    counter_streams = dict()
    for name, stream in scan.streams.items():
        if stream.encoding["type"] == "json" and "lima" in stream.info["format"]:
            if name.split(":")[-2] in lima_names:
                lima_streams[name] = stream
                lima_clients[name] = lima_client_factory(data_store, stream.info)
        elif name.split(":")[-1] in counter_names:
            counter_streams[name] = stream

    client = StreamingClient({**lima_streams, **counter_streams})
    lima_buffer_count = Counter()

    while True:
        try:
            output = client.read()
        except EndOfStream:
            break
        for stream, (_, payload) in output.items():
            name_parts = stream.name.split(":")
            if stream.name in lima_streams:
                # payload is a sequence of JSON statuses
                ctr_name = name_parts[-2]
                last_status = payload[-1]
                lima_client = lima_clients[stream.name]
                lima_client.update(**last_status)
                n_already_read = lima_buffer_count[ctr_name]
                try:
                    data = lima_client[n_already_read:]
                except IndexNoMoreThereError:
                    continue
                buffers[ctr_name].extend(data)
                lima_buffer_count[ctr_name] += len(data)
            else:
                # payload is a sequence of data points (0D, 1D, 2D)
                ctr_name = name_parts[-1]
                buffers[ctr_name].extend(payload)

        nyield = min(len(v) for v in buffers.values())
        if nyield:
            for i in range(nyield):
                yield {name: values[i] for name, values in buffers.items()}
            buffers = {name: values[nyield:] for name, values in buffers.items()}


def last_lima_image(channel_info: dict) -> ArrayLike:
    """Get last lima image from memory"""
    data_store = _get_data_store()
    lima_client = lima_client_factory(data_store, channel_info)
    return lima_client.get_last_live_image().array


def _get_data_store() -> None:
    redis_url = BeaconData().get_redis_data_db()
    return DataStore(redis_url)
