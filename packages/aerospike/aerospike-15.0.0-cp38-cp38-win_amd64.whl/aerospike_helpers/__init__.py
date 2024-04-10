##########################################################################
# Copyright 2013-2021 Aerospike, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################


# start delvewheel patch
def _delvewheel_patch_1_5_4():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-aerospike-15.0.0')
        if os.path.isfile(load_order_filepath):
            with open(os.path.join(libs_dir, '.load-order-aerospike-15.0.0')) as file:
                load_order = file.read().split()
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(ctypes.c_wchar_p(lib_path), None, 0x00000008):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_5_4()
del _delvewheel_patch_1_5_4
# end delvewheel patch

class HyperLogLog(bytes):
    """
    Represents a HyperLogLog value. This can be returned from the server or created in order to be sent to the server.

    The constructor takes in any argument that the :class:`bytes` constructor takes in.

    >>> h = HyperLogLog([1, 2, 3])
    >>> client.put(key, {"hyperloglog": h})
    """
    def __new__(cls, o) -> "HyperLogLog":
        return super().__new__(cls, o)
