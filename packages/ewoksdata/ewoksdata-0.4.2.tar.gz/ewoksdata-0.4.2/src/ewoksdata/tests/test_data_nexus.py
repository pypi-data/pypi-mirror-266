from ..data import nexus


def test_create_nexus_group(tmpdir):
    with nexus.create_nexus_group(str(tmpdir / "file.h5")) as (h5item, already_existed):
        assert not already_existed
        assert h5item.name == "/results"
    with nexus.create_nexus_group(str(tmpdir / "file.h5")) as (h5item, already_existed):
        assert already_existed
        assert h5item.name == "/results"

    with nexus.create_nexus_group(
        str(tmpdir / "file.h5::/c"), default_levels=("a", "b")
    ) as (h5item, already_existed):
        assert not already_existed
        assert h5item.name == "/c/b"
    with nexus.create_nexus_group(
        str(tmpdir / "file.h5::/c"), default_levels=("a", "b")
    ) as (h5item, already_existed):
        assert already_existed
        assert h5item.name == "/c/b"
    with nexus.create_nexus_group(str(tmpdir / "file.h5::/c/b")) as (
        h5item,
        already_existed,
    ):
        assert already_existed
        assert h5item.name == "/c/b"
