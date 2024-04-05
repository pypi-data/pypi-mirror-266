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

import importlib
from pathlib import Path

import click


class SuperIDECLI(click.MultiCommand):
    leftover_args = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._root_path = Path(__file__).parent
        self._cmd_aliases = dict(package="pkg")

    def _find_commands(self):
        def _to_module_path(p):
            return (
                "superide." + ".".join(p.relative_to(self._root_path).parts)[:-3]
            )

        result = {}
        # rglob() 方法是 pathlib 模块中的一个方法，用于递归地查找文件和文件夹。
        for p in self._root_path.rglob("cli.py"):
            # skip this module
            if p.parent == self._root_path:
                continue
            cmd_name = p.parent.name
            result[self._cmd_aliases.get(cmd_name, cmd_name)] = _to_module_path(p)

        return result

    @staticmethod
    def in_silence():
        args = SuperIDECLI.leftover_args
        return args and any(
            [
                args[0] == "debug" and "--interpreter" in " ".join(args),
                args[0] == "upgrade",
                "--json-output" in args,
                "--version" in args,
            ]
        )

    @classmethod
    def reveal_cmd_path_args(cls, ctx):
        result = []
        group = ctx.command
        args = cls.leftover_args[::]
        while args:
            cmd_name = args.pop(0)
            next_group = group.get_command(ctx, cmd_name)
            if next_group:
                group = next_group
                result.append(cmd_name)
            if not hasattr(group, "get_command"):
                break
        return result

    def invoke(self, ctx):
        SuperIDECLI.leftover_args = ctx.args
        if hasattr(ctx, "protected_args"):
            SuperIDECLI.leftover_args = ctx.protected_args + ctx.args
        return super().invoke(ctx)

    def list_commands(self, ctx):
        return sorted(list(self._find_commands()))

    def get_command(self, ctx, cmd_name):
        commands = self._find_commands()
        if cmd_name not in commands:
            return self._handle_aliases_command(ctx, cmd_name)
        module = importlib.import_module(commands[cmd_name])
        return getattr(module, "cli")

    @staticmethod
    def _handle_aliases_command(ctx, cmd_name):
        # pylint: disable=import-outside-toplevel
        if cmd_name == "init":
            from superide.project.commands.init import project_init_cmd

            return project_init_cmd

        if cmd_name == "pull":
            from superide.registry.cli import cli

            return cli

        raise click.UsageError('No such command "%s"' % cmd_name, ctx)
