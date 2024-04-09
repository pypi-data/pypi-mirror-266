from ..data import hdf5


def test_bliss_data(bliss_scan):
    with hdf5.h5context(bliss_scan) as f:
        values = f["/2.1/measurement/diode1"][()]
        assert values.tolist() == list(range(31))
        values = f["/2.1/measurement/diode2"][()]
        assert values.tolist() == list(range(31))
        values = f["/2.1/measurement/p3"][:, 0, 0]
        assert values.tolist() == list(range(31))
        values = f["/2.1/measurement/p3"][:, -1, -1]
        assert values.tolist() == list(range(31))
