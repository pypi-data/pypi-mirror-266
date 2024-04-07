"""
Plyvel, a fast and feature-rich Python interface to LevelDB.
"""


# start delvewheel patch
def _delvewheel_patch_1_5_4():
    import os
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'plyvel_ci.libs'))
    if os.path.isdir(libs_dir):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_5_4()
del _delvewheel_patch_1_5_4
# end delvewheel patch

# Only import the symbols that are part of the public API
from ._plyvel import (  # noqa
    __leveldb_version__,
    DB,
    repair_db,
    destroy_db,
    Error,
    IOError,
    CorruptionError,
    IteratorInvalidError,
)

from ._version import __version__  # noqa