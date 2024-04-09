from .exceptions import VersionError

try:
    # blissdata >=1
    from .blissdatav1 import iter_bliss_scan_data_from_memory
    from .blissdatav1 import last_lima_image
    from blissdata.h5api import dynamic_hdf5
except VersionError as exc:
    try:
        # blissdata >0.3.3,<1 (unreleased, branch id31_2.0)
        from .blissdatavid31 import iter_bliss_scan_data_from_memory
        from .blissdatavid31 import last_lima_image
        from blissdata.h5api import dynamic_hdf5
    except VersionError:
        try:
            # blissdata <=0.3.3
            from .blissdatav0 import iter_bliss_scan_data_from_memory
            from .blissdatav0 import last_lima_image
            from blissdata.h5api import dynamic_hdf5
        except VersionError:  # noqa F841
            _EXC = exc

            def _reraise(*_, **kw):
                raise _EXC

            class BlissDataVersionNotSupported:
                def __getattr__(self, *_):
                    return _reraise

            dynamic_hdf5 = BlissDataVersionNotSupported()

            def iter_bliss_scan_data_from_memory(*_, **kw):
                raise _EXC

            def last_lima_image(*_, **kw):
                raise _EXC
