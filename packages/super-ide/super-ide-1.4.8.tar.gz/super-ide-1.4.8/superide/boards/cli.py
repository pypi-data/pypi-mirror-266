# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import shutil
import os

import click
from tabulate import tabulate

from superide import fs



@click.command("boards", short_help="Board Explorer")
@click.argument("query", required=False)
@click.option("--json-output", is_flag=True)
def cli(query, json_output):  # pylint: disable=R0912
    if json_output:
        return _print_boards_json(query)

    grpboards = {}
    for board in _get_boards():
        if query and not any(
            query.lower() in str(board.get(k, "")).lower()
            for k in ("id", "name", "mcu", "vendor", "platform", "frameworks")
        ):
            continue
        if board["platform"] not in grpboards:
            grpboards[board["platform"]] = []
        grpboards[board["platform"]].append(board)

    terminal_width = shutil.get_terminal_size().columns
    for platform, boards in sorted(grpboards.items()):
        click.echo("")
        click.echo("Platform: ", nl=False)
        click.secho(platform, bold=True)
        click.echo("=" * terminal_width)
        print_boards(boards)
    return True


def print_boards(boards):
    click.echo(
        tabulate(
            [
                (
                    click.style(b["id"], fg="cyan"),
                    b["mcu"],
                    "%dMHz" % (b["fcpu"] / 1000000),
                    fs.humanize_file_size(b["rom"]),
                    fs.humanize_file_size(b["ram"]),
                    b["name"],
                )
                for b in boards
            ],
            headers=["ID", "MCU", "Frequency", "Flash", "RAM", "Name"],
        )
    )


def _get_boards():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    boards_json_path = os.path.join(current_dir,'boards.json')
    return get_boards_json(boards_json_path)
#    return get_boards_json('./boards.json')


def _print_boards_json(query):
    result = _get_boards()
    click.echo(json.dumps(result))


def get_boards_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
        # with open(file_path, 'r', encoding='utf-16') as file:
            json_data = json.load(file)  # 解析JSON数据
            return json_data
    except FileNotFoundError:
        print(f"文件 '{file_path}' 未找到")
    except json.JSONDecodeError as e:
        print("JSON解析异常:", e)
