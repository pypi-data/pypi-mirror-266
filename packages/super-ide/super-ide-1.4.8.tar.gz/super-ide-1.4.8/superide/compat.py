# Copyright (c) Mengning Software. 2023. All rights reserved.
#
# Super IDE licensed under GNU Affero General Public License v3 (AGPL-3.0) .
# You can use this software according to the terms and conditions of the AGPL-3.0.
# You may obtain a copy of AGPL-3.0 at:
#
#    https://www.gnu.org/licenses/agpl-3.0.txt
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the AGPL-3.0 for more details.

# pylint: disable=unused-import,no-name-in-module

import importlib.util
import inspect
import locale
import shlex
import sys

from superide.exception import UserSideException

if sys.version_info >= (3, 7):
    from asyncio import create_task as aio_create_task
    from asyncio import get_running_loop as aio_get_running_loop
else:
    from asyncio import ensure_future as aio_create_task
    from asyncio import get_event_loop as aio_get_running_loop


if sys.version_info >= (3, 8):
    from shlex import join as shlex_join
else:

    def shlex_join(split_command):
        return " ".join(shlex.quote(arg) for arg in split_command)


if sys.version_info >= (3, 9):
    from asyncio import to_thread as aio_to_thread
# else:
#     from starlette.concurrency import run_in_threadpool as aio_to_thread


PY2 = sys.version_info[0] == 2  # DO NOT REMOVE IT. ESP8266/ESP32 depend on it
IS_CYGWIN = sys.platform.startswith("cygwin")
IS_WINDOWS = WINDOWS = sys.platform.startswith("win")
IS_MACOS = sys.platform.startswith("darwin")
MISSING = object()
string_types = (str,)


def is_bytes(x):
    return isinstance(x, (bytes, memoryview, bytearray))


def isascii(text):
    if sys.version_info >= (3, 7):
        return text.isascii()
    for c in text or "":
        if ord(c) > 127:
            return False
    return True


def is_terminal():
    try:
        return sys.stdout.isatty()
    except Exception:  # pylint: disable=broad-except
        return False


def ci_strings_are_equal(a, b):
    if a == b:
        return True
    if not a or not b:
        return False
    return a.strip().lower() == b.strip().lower()


def hashlib_encode_data(data):
    if is_bytes(data):
        return data
    if not isinstance(data, string_types):
        data = str(data)
    return data.encode()


def load_python_module(name, pathname):
    spec = importlib.util.spec_from_file_location(name, pathname)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_filesystem_encoding():
    return sys.getfilesystemencoding() or sys.getdefaultencoding()


def get_locale_encoding():
    return locale.getpreferredencoding()


def get_object_members(obj, ignore_private=True):
    members = inspect.getmembers(obj, lambda a: not inspect.isroutine(a))
    if not ignore_private:
        return members
    return {
        item[0]: item[1]
        for item in members
        if not (item[0].startswith("__") and item[0].endswith("__"))
    }


def ensure_python3(raise_exception=True):
    compatible = sys.version_info >= (3, 6)
    if not raise_exception or compatible:
        return compatible
    raise UserSideException(
        "Python 3.6 or later is required for this operation. \n"
        "Please check a migration guide:\n"
        "https://gitee.com/SuperIDE/super-ide"
    )


def path_to_unicode(path):
    """
    Deprecated: Compatibility with dev-platforms,
    and custom device monitor filters
    """
    return path
