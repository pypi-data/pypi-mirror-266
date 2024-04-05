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

import click

from superide.project.commands.config import project_config_cmd
from superide.project.commands.init import project_init_cmd
from superide.project.commands.metadata import project_metadata_cmd


@click.group(
    "project",
    commands=[
        project_config_cmd,
        project_init_cmd,
        project_metadata_cmd,
    ],
    short_help="Project Manager",
)
def cli():
    pass
