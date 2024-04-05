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

from os import makedirs
from os.path import isdir, isfile, join

from superide import fs
from superide.project.helpers import compute_project_checksum, get_project_dir

KNOWN_CLEAN_TARGETS = ("clean",)
KNOWN_FULLCLEAN_TARGETS = ("cleanall", "fullclean")
KNOWN_ALLCLEAN_TARGETS = KNOWN_CLEAN_TARGETS + KNOWN_FULLCLEAN_TARGETS


def clean_build_dir(build_dir, config):
    # remove legacy ".pioenvs" folder
    legacy_build_dir = join(get_project_dir(), ".pioenvs")
    if isdir(legacy_build_dir) and legacy_build_dir != build_dir:
        fs.rmtree(legacy_build_dir)

    checksum_file = join(build_dir, "project.checksum")
    checksum = compute_project_checksum(config)

    if isdir(build_dir):
        # check project structure
        if isfile(checksum_file):
            with open(checksum_file, encoding="utf8") as fp:
                if fp.read() == checksum:
                    return
        fs.rmtree(build_dir)

    makedirs(build_dir)
    with open(checksum_file, mode="w", encoding="utf8") as fp:
        fp.write(checksum)
