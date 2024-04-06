""" pynchon.util.testing
"""

from pathlib import Path

from pynchon.abcs import AttrDict


def get_test_info(fname: str) -> dict:
    """

    :param fname: str:
    :param fname: str:

    """
    suite_dir = Path(fname).relative_to(Path.cwd()).parents[0]
    test_root = suite_dir.parents[0]
    return AttrDict(
        root=test_root,
        suite=AttrDict(path=suite_dir, name=suite_dir.name),
        fixtures=AttrDict(path=test_root / "fixtures"),
    )
