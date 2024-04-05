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

from superide.system.commands.completion import system_completion_cmd
from superide.system.commands.info import system_info_cmd
# from superide.system.commands.prune import system_prune_cmd


@click.group(
    "system",
    commands=[
        system_completion_cmd,
        system_info_cmd,
        # system_prune_cmd,
    ],
    short_help="Miscellaneous system commands",
)
def cli():
    pass
