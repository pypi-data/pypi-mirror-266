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

import glob
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys

import click

from superide import exception
from superide.compat import IS_WINDOWS


class cd:
    def __init__(self, new_path):
        self.new_path = new_path
        self.prev_path = os.getcwd()

    def __enter__(self):
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.prev_path)


def get_source_dir():
    curpath = os.path.abspath(__file__)
    if not os.path.isfile(curpath):
        for p in sys.path:
            if os.path.isfile(os.path.join(p, __file__)):
                curpath = os.path.join(p, __file__)
                break
    return os.path.dirname(curpath)


def get_assets_dir():
    return os.path.join(get_source_dir(), "assets")


def load_json(file_path):
    try:
        with open(file_path, mode="r", encoding="utf8") as f:
            return json.load(f)
    except ValueError as exc:
        raise exception.InvalidJSONFile(file_path) from exc


def humanize_file_size(filesize):
    base = 1024
    unit = 0
    suffix = "B"
    filesize = float(filesize)
    if filesize < base:
        return "%d%s" % (filesize, suffix)
    for i, suffix in enumerate("KMGTPEZY"):
        unit = base ** (i + 2)
        if filesize >= unit:
            continue
        if filesize % (base ** (i + 1)):
            return "%.2f%sB" % ((base * filesize / unit), suffix)
        break
    return "%d%sB" % ((base * filesize / unit), suffix)


def calculate_file_hashsum(algorithm, path):
    h = hashlib.new(algorithm)
    with io.open(path, "rb", buffering=0) as fp:
        while True:
            chunk = fp.read(io.DEFAULT_BUFFER_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def calculate_folder_size(path):
    assert os.path.isdir(path)
    result = 0
    for root, __, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            if not os.path.islink(file_path):
                result += os.path.getsize(file_path)
    return result


def get_superide_udev_rules_path():
    return os.path.abspath(
        os.path.join(get_assets_dir(), "system", "99-superide-udev.rules")
    )


def ensure_udev_rules():
    from superide.util import get_systype  # pylint: disable=import-outside-toplevel

    def _rules_to_set(rules_path):
        result = set()
        with open(rules_path, encoding="utf8") as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                result.add(line)
        return result

    if "linux" not in get_systype():
        return None
    installed_rules = [
        "/etc/udev/rules.d/99-superide-udev.rules",
        "/lib/udev/rules.d/99-superide-udev.rules",
    ]
    if not any(os.path.isfile(p) for p in installed_rules):
        raise exception.MissedUdevRules

    origin_path = get_superide_udev_rules_path()
    if not os.path.isfile(origin_path):
        return None

    origin_rules = _rules_to_set(origin_path)
    for rules_path in installed_rules:
        if not os.path.isfile(rules_path):
            continue
        current_rules = _rules_to_set(rules_path)
        if not origin_rules <= current_rules:
            raise exception.OutdatedUdevRules(rules_path)

    return True


def path_endswith_ext(path, extensions):
    if not isinstance(extensions, (list, tuple)):
        extensions = [extensions]
    for ext in extensions:
        if path.endswith("." + ext):
            return True
    return False


def match_src_files(src_dir, src_filter=None, src_exts=None, followlinks=True):
    def _add_candidate(items, item, src_dir):
        if not src_exts or path_endswith_ext(item, src_exts):
            items.add(os.path.relpath(item, src_dir))

    def _find_candidates(pattern):
        candidates = set()
        for item in glob.glob(
            os.path.join(glob.escape(src_dir), pattern), recursive=True
        ):
            if not os.path.isdir(item):
                _add_candidate(candidates, item, src_dir)
                continue
            for root, dirs, files in os.walk(item, followlinks=followlinks):
                for d in dirs if not followlinks else []:
                    if os.path.islink(os.path.join(root, d)):
                        _add_candidate(candidates, os.path.join(root, d), src_dir)
                for f in files:
                    _add_candidate(candidates, os.path.join(root, f), src_dir)
        return candidates

    src_filter = src_filter or ""
    if isinstance(src_filter, (list, tuple)):
        src_filter = " ".join(src_filter)

    result = set()
    # correct fs directory separator
    src_filter = src_filter.replace("/", os.sep).replace("\\", os.sep)
    for action, pattern in re.findall(r"(\+|\-)<([^>]+)>", src_filter):
        candidates = _find_candidates(pattern)
        if action == "+":
            result |= candidates
        else:
            result -= candidates
    return sorted(list(result))


def to_unix_path(path):
    if not IS_WINDOWS or not path:
        return path
    return path.replace("\\", "/")


def expanduser(path):
    """
    Be compatible with Python 3.8, on Windows skip HOME and check for USERPROFILE
    """
    if not IS_WINDOWS or not path.startswith("~") or "USERPROFILE" not in os.environ:
        return os.path.expanduser(path)
    return os.environ["USERPROFILE"] + path[1:]


def change_filemtime(path, mtime):
    os.utime(path, (mtime, mtime))


def rmtree(path):
    def _onerror(func, path, __):
        try:
            st_mode = os.stat(path).st_mode
            if st_mode & stat.S_IREAD:
                os.chmod(path, st_mode | stat.S_IWRITE)
            func(path)
        except Exception as exc:  # pylint: disable=broad-except
            click.secho(
                "%s \nPlease manually remove the file `%s`" % (str(exc), path),
                fg="red",
                err=True,
            )

    return shutil.rmtree(path, onerror=_onerror)
