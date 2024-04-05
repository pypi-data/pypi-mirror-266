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

import os
import random
from glob import glob

import pytest

from superide import __configfile__
from superide import fs, proc
from superide.package.manager.platform import PlatformPackageManager
from superide.platform.factory import PlatformFactory
from superide.project.config import ProjectConfig
from superide.project.exception import ProjectError


def pytest_generate_tests(metafunc):
    if "pioproject_dir" not in metafunc.fixturenames:
        return
    examples_dirs = []

    # repo examples
    examples_dirs.append(
        os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    )

    # dev/platforms
    for pkg in PlatformPackageManager().get_installed():
        p = PlatformFactory.new(pkg)
        examples_dir = os.path.join(p.get_dir(), "examples")
        if os.path.isdir(examples_dir):
            examples_dirs.append(examples_dir)

    project_dirs = []
    for examples_dir in examples_dirs:
        candidates = {}
        for root, _, files in os.walk(examples_dir):
            if __configfile__ not in files or ".skiptest" in files:
                continue
            if "mbed-legacy-examples" in root:
                continue
            group = os.path.basename(root)
            if "-" in group:
                group = group.split("-", 1)[0]
            if group not in candidates:
                candidates[group] = []
            candidates[group].append(root)

        project_dirs.extend(
            [random.choice(examples) for examples in candidates.values() if examples]
        )

    metafunc.parametrize("pioproject_dir", sorted(project_dirs))


def test_run(pioproject_dir):
    with fs.cd(pioproject_dir):
        config = ProjectConfig()

        # temporary fix for unreleased dev-platforms with broken env name
        try:
            config.validate()
        except ProjectError as exc:
            pytest.skip(str(exc))

        build_dir = config.get("superide", "build_dir")
        if os.path.isdir(build_dir):
            fs.rmtree(build_dir)

        env_names = config.envs()
        result = proc.exec_command(
            ["superide", "run", "-e", random.choice(env_names)]
        )
        if result["returncode"] != 0:
            pytest.fail(str(result))

        assert os.path.isdir(build_dir)

        # check .elf file
        for item in os.listdir(build_dir):
            if not os.path.isdir(item):
                continue
            assert os.path.isfile(os.path.join(build_dir, item, "firmware.elf"))
            # check .hex or .bin files
            firmwares = []
            for ext in ("bin", "hex"):
                firmwares += glob(os.path.join(build_dir, item, "firmware*.%s" % ext))
            if not firmwares:
                pytest.fail("Missed firmware file")
            for firmware in firmwares:
                assert os.path.getsize(firmware) > 0
