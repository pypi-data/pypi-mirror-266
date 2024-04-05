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


import json
import platform
import sys

import click
from tabulate import tabulate

from superide import __version__, compat, proc, util
# from superide.package.manager.library import LibraryPackageManager
# from superide.package.manager.platform import PlatformPackageManager
# from superide.package.manager.tool import ToolPackageManager
from superide.project.config import ProjectConfig


@click.command("info", short_help="Display system-wide information")
@click.option("--json-output", is_flag=True)
def system_info_cmd(json_output):
    project_config = ProjectConfig()
    data = {}
    data["core_version"] = {"title": "superide Core", "value": __version__}
    data["python_version"] = {
        "title": "Python",
        "value": "{0}.{1}.{2}-{3}.{4}".format(*list(sys.version_info)),
    }
    data["system"] = {"title": "System Type", "value": util.get_systype()}
    data["platform"] = {"title": "Platform", "value": platform.platform(terse=True)}
    data["filesystem_encoding"] = {
        "title": "File System Encoding",
        "value": compat.get_filesystem_encoding(),
    }
    data["locale_encoding"] = {
        "title": "Locale Encoding",
        "value": compat.get_locale_encoding(),
    }
    data["core_dir"] = {
        "title": "superide Core Directory",
        "value": project_config.get("superide", "core_dir"),
    }
    data["platformio_exe"] = {
        "title": "superide Core Executable",
        "value": proc.where_is_program(
            "superide.exe" if compat.IS_WINDOWS else "superide"
        ),
    }
    data["python_exe"] = {
        "title": "Python Executable",
        "value": proc.get_pythonexe_path(),
    }
    # data["global_lib_nums"] = {
    #     "title": "Global Libraries",
    #     "value": len(LibraryPackageManager().get_installed()),
    # }
    # data["dev_platform_nums"] = {
    #     "title": "Development Platforms",
    #     "value": len(PlatformPackageManager().get_installed()),
    # }
    # data["package_tool_nums"] = {
    #     "title": "Tools & Toolchains",
    #     "value": len(
    #         ToolPackageManager(
    #             project_config.get("superide", "packages_dir")
    #         ).get_installed()
    #     ),
    # }
    click.echo(
        json.dumps(data)
        if json_output
        else tabulate([(item["title"], item["value"]) for item in data.values()])
    )
