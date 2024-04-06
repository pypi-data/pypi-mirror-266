""" pynchon.util.text CLI
"""

from pynchon.cli import common

from pynchon.util import lme, typing  # noqa

LOGGER = lme.get_logger(__name__)
entry = common.entry_for(__name__)

# if child folders define __main__, consume entry-groups from those places
common.load_groups_from_children(root="pynchon.util.text", parent=entry)

if __name__ == "__main__":
    entry()
