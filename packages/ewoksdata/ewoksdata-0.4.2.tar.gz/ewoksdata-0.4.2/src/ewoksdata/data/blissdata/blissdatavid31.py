from numbers import Number
from collections import Counter
from typing import List, Optional

from numpy.typing import ArrayLike

from .exceptions import VersionError

try:
    from blissdata.redis_engine.scan import Scan
    from blissdata.redis_engine.stream import StreamingClient
    from blissdata.redis_engine.models import ScanState
    from blissdata.redis_engine.exceptions import EndOfStream
    from blissdata.lima.client import lima_client_factory
    from blissdata.beacon.data import BeaconData
    from blissdata import redis_engine
except ImportError as e:
    raise VersionError(str(e)) from e


def iter_bliss_scan_data_from_memory(
    db_name: str,
    lima_names: List[str],
    counter_names: List[str],
    retry_timeout: Optional[Number] = None,
    retry_period: Optional[Number] = None,
):
    _ensure_redis()
    scan = Scan.load(db_name)
    buffers = {name: list() for name in lima_names + counter_names}

    while scan.state < ScanState.PREPARED:
        scan.update()
    if scan.state is ScanState.ABORTED:
        return

    lima_streams = dict()
    lima_clients = dict()
    lima_buffer_count = dict()
    counter_streams = dict()
    for name, stream in scan.streams.items():
        if stream.encoding["type"] == "json" and "lima" in stream.info["format"]:
            if name.split(":")[-2] in lima_names:
                lima_streams[name] = stream
                lima_clients[name] = lima_client_factory(stream.info)
                lima_buffer_count[name] = 0
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
                lima_client = lima_clients[stream.name]
                lima_client.update(**payload[-1])
                n_already_read = lima_buffer_count[ctr_name]
                data = lima_client[n_already_read:]
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
    _ensure_redis()
    lima_client = lima_client_factory(channel_info)
    return lima_client.get_last_live_image().array


def _ensure_redis() -> None:
    url = BeaconData().get_redis_data_db()
    current_url = _current_redis_url()
    if current_url:
        if url == current_url:
            return
        raise RuntimeError("The Redis URL has changed. Restart the Nexus writer.")
    redis_engine.set_redis_url(url)


def _current_redis_url() -> Optional[str]:
    if redis_engine._redis is None:
        return
    kwargs = redis_engine._redis.connection_pool.connection_kwargs
    if "path" in kwargs:
        return f"unix://{kwargs['path']}"
    else:
        return f"redis://{kwargs['host']}:{kwargs['port']}"
