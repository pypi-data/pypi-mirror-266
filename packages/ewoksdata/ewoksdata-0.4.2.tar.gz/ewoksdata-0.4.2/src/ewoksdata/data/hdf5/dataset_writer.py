import time
from typing import Optional, List

import h5py
import numpy
from numpy.typing import ArrayLike

from .types import StrictPositiveIntegral
from .config import guess_dataset_config


class _DatasetWriterBase:
    def __init__(
        self,
        parent: h5py.Group,
        name: str,
        attrs: Optional[dict] = None,
        flush_period: Optional[float] = None,
    ) -> None:
        self._parent = parent
        self._name = name
        self._attrs = attrs
        self._dataset_name = f"{parent.name}/{name}"
        self._dataset = None
        self._flush_period = flush_period
        self._last_flush = None

    @property
    def dataset_name(self) -> str:
        return self._dataset_name

    def __enter__(self) -> "_DatasetWriterBase":
        return self

    def __exit__(self, *args) -> None:
        self.flush_buffer()

    @property
    def dataset(self) -> Optional[h5py.Dataset]:
        return self._dataset

    def _create_dataset(self, first_data_point: numpy.ndarray) -> h5py.Dataset:
        raise NotImplementedError

    def flush_buffer(self, align: bool = False) -> bool:
        raise NotImplementedError

    def _flush_time_expired(self) -> bool:
        if self._flush_period is None:
            return False
        if self._last_flush is None:
            self._last_flush = time.time()
            return False
        return (time.time() - self._last_flush) >= self._flush_period


class DatasetWriter(_DatasetWriterBase):
    def __init__(
        self,
        parent: h5py.Group,
        name: str,
        npoints: Optional[StrictPositiveIntegral] = None,
        attrs: Optional[dict] = None,
        flush_period: Optional[float] = None,
    ) -> None:
        super().__init__(parent, name, attrs=attrs, flush_period=flush_period)
        self._npoints = npoints
        self._buffer: List[ArrayLike] = list()
        self._npoints_added: int = 0
        self._chunked: bool = False
        self._nchunk: int = 0
        self._nflushed: int = 0

    def _create_dataset(self, first_data_point: numpy.ndarray) -> h5py.Dataset:
        scan_shape = (self._npoints,)
        detector_shape = first_data_point.shape
        dtype = first_data_point.dtype
        if self._npoints is None:
            max_shape = scan_shape + detector_shape
            shape = (1,) + first_data_point.shape
        else:
            max_shape = None
            shape = scan_shape + first_data_point.shape

        options = guess_dataset_config(
            scan_shape, detector_shape, dtype=dtype, max_shape=max_shape
        )
        options["shape"] = shape
        options["dtype"] = dtype
        options["fillvalue"] = numpy.nan  # converts to 0 for integers
        if max_shape:
            options["maxshape"] = max_shape
        if options["chunks"]:
            self._chunked = True
            self._nchunk = options["chunks"][0]
        dset = self._parent.create_dataset(self._name, **options)
        if self._attrs:
            dset.attrs.update(self._attrs)
        return dset

    @property
    def npoints_added(self) -> int:
        return self._npoints_added

    def add_point(self, data: ArrayLike) -> bool:
        if self._dataset is None:
            self._dataset = self._create_dataset(data)
        self._buffer.append(data)
        self._npoints_added += 1
        return self.flush_buffer(align=True)

    def add_points(self, data: ArrayLike) -> bool:
        if self._dataset is None:
            self._dataset = self._create_dataset(data[0])
        self._buffer.extend(data)
        self._npoints_added += len(data)
        return self.flush_buffer(align=True)

    def flush_buffer(self, align: bool = False) -> bool:
        # Determine how many points to flush
        nbuffer = len(self._buffer)
        if self._flush_time_expired():
            nflush = nbuffer
        elif align and self._chunked:
            n = nbuffer + (self._nflushed % self._nchunk)
            nflush = n // self._nchunk * self._nchunk
            nflush = min(nflush, nbuffer)
        else:
            nflush = nbuffer
        if nflush == 0:
            return False

        # Enlarge the dataset when needed
        nalloc = self._dataset.shape[0]
        istart = self._nflushed
        nflushed = istart + nflush
        if self._chunked and nflushed > nalloc:
            self._dataset.resize(nflushed, axis=0)

        # Move data from memory to HDF5
        self._dataset[istart : istart + nflush] = self._buffer[:nflush]
        self._buffer = self._buffer[nflush:]
        self._nflushed = nflushed

        self._last_flush = time.time()
        return True


class StackDatasetWriter(_DatasetWriterBase):
    def __init__(
        self,
        parent: h5py.Group,
        name: str,
        npoints: Optional[StrictPositiveIntegral] = None,
        nstack: Optional[StrictPositiveIntegral] = None,
        attrs: Optional[dict] = None,
        flush_period: Optional[float] = None,
    ) -> None:
        super().__init__(parent, name, attrs=attrs, flush_period=flush_period)
        self._npoints = npoints
        self._nstack = nstack
        self._buffers: List[List[ArrayLike]] = list()
        self._chunked: bool = False
        self._nchunk: ArrayLike = numpy.zeros(2, dtype=int)
        self._nflushed: ArrayLike = numpy.array(list(), dtype=int)

    def _create_dataset(
        self, first_data_point: numpy.ndarray, stack_index: int
    ) -> h5py.Dataset:
        scan_shape = (self._nstack, self._npoints)
        detector_shape = first_data_point.shape
        dtype = first_data_point.dtype
        if self._npoints is None or self._nstack is None:
            max_shape = scan_shape + detector_shape
            shape = (stack_index + 1, 1) + first_data_point.shape
        else:
            max_shape = None
            shape = scan_shape + first_data_point.shape

        options = guess_dataset_config(
            scan_shape, detector_shape, dtype=dtype, max_shape=max_shape
        )
        options["shape"] = shape
        options["dtype"] = dtype
        options["fillvalue"] = numpy.nan  # converts to 0 for integers
        if max_shape:
            options["maxshape"] = max_shape
        if options["chunks"]:
            self._chunked = True
            self._nchunk = numpy.array(options["chunks"][:2], dtype=int)
        dset = self._parent.create_dataset(self._name, **options)
        if self._attrs:
            dset.attrs.update(self._attrs)
        return dset

    def _get_buffer(self, stack_index: int) -> List[ArrayLike]:
        for _ in range(max(stack_index - len(self._buffers) + 1, 0)):
            self._buffers.append(list())
            self._nflushed = numpy.append(self._nflushed, 0)
        return self._buffers[stack_index]

    def add_point(self, data: ArrayLike, stack_index: int) -> bool:
        if self._dataset is None:
            self._dataset = self._create_dataset(data, stack_index)
        buffer = self._get_buffer(stack_index)
        buffer.append(data)
        return self.flush_buffer(align=True)

    def add_points(self, data: ArrayLike, stack_index: int) -> bool:
        if self._dataset is None:
            self._dataset = self._create_dataset(data[0], stack_index)
        buffer = self._get_buffer(stack_index)
        buffer.extend(data)
        return self.flush_buffer(align=True)

    def flush_buffer(self, align: bool = False) -> bool:
        # Determine how many points to flush for each buffer in the stack
        nbuffer = numpy.array([len(buffer) for buffer in self._buffers])
        nchunk_dim0, nchunk_dim1 = self._nchunk[:2]
        if self._flush_time_expired():
            nflush = nbuffer
        elif align and self._chunked:
            n = nbuffer + (self._nflushed % nchunk_dim1)
            nflush = n // nchunk_dim1 * nchunk_dim1
            nflush = numpy.minimum(nflush, nbuffer)
            for i0_chunk0 in range(0, len(nbuffer), nchunk_dim0):
                nflush[i0_chunk0 : i0_chunk0 + nchunk_dim0] = min(
                    nflush[i0_chunk0 : i0_chunk0 + nchunk_dim0]
                )
        else:
            nflush = nbuffer
        if not any(nflush):
            return False

        # Enlarge the dataset when needed
        nalloc = self._dataset.shape[:2]
        istart = self._nflushed
        nflushed = istart + nflush
        nalloc_new = numpy.array([len(nbuffer), max(nflushed)])
        if self._chunked and any(nalloc_new > nalloc):
            for axis, n in enumerate(nalloc_new):
                self._dataset.resize(n, axis=axis)

        # Move data from memory to HDF5
        if nchunk_dim0 == 0:
            nchunk_dim0 = len(nbuffer)
        for i0_chunk0 in range(0, len(nbuffer), nchunk_dim0):
            idx_dim0 = slice(i0_chunk0, i0_chunk0 + nchunk_dim0)
            nflush_dim1 = nflush[idx_dim0]
            istart0_dim1 = istart[idx_dim0]
            buffers = self._buffers[idx_dim0]
            if all(nflush_dim1 == nflush_dim1[0]) and all(
                istart0_dim1 == istart0_dim1[0]
            ):
                data = [buffer[: nflush_dim1[0]] for buffer in buffers]
                idx_dim1 = slice(istart0_dim1[0], istart0_dim1[0] + nflush_dim1[0])
                self._dataset[idx_dim0, idx_dim1] = data
            else:
                for buffer, i_dim0, istart_dim1, n_dim1 in zip(
                    buffers,
                    range(i0_chunk0, i0_chunk0 + nchunk_dim0),
                    istart0_dim1,
                    nflush_dim1,
                ):
                    self._dataset[i_dim0, istart_dim1 : istart_dim1 + n_dim1, ...] = (
                        buffer[:n_dim1]
                    )
        self._buffers = [
            buffer[n_dim1:] for buffer, n_dim1 in zip(self._buffers, nflush)
        ]
        self._nflushed = nflushed

        self._last_flush = time.time()
        return True
