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
import sys
import traceback

import click

from superide import __version__, exception, maintenance
from superide.cli import SuperIDECLI
from superide.compat import IS_CYGWIN, ensure_python3


@click.command(
    cls=SuperIDECLI, context_settings=dict(help_option_names=["-h", "--help"])
)
@click.version_option(__version__, prog_name="Super-IDE Core")
@click.option("--force", "-f", is_flag=True, help="DEPRECATED", hidden=True)
@click.option("--caller", "-c", help="Caller ID (service)")
@click.option("--no-ansi", is_flag=True, help="Do not print ANSI control characters")
@click.pass_context
def cli(ctx, force, caller, no_ansi):  # pylint: disable=unused-argument
    try:
        if (
            no_ansi
            or str(
                os.getenv("PLATFORMIO_NO_ANSI", os.getenv("PLATFORMIO_DISABLE_COLOR"))
            ).lower()
            == "true"
        ):
            # pylint: disable=protected-access
            click._compat.isatty = lambda stream: False
        elif (
            str(
                os.getenv("PLATFORMIO_FORCE_ANSI", os.getenv("PLATFORMIO_FORCE_COLOR"))
            ).lower()
            == "true"
        ):
            # pylint: disable=protected-access
            click._compat.isatty = lambda stream: True
    except:  # pylint: disable=bare-except
        pass

    maintenance.on_cmd_start(ctx, caller)


@cli.result_callback()
@click.pass_context
def process_result(*_, **__):
    maintenance.on_cmd_end()


def configure():
    if IS_CYGWIN:
        raise exception.CygwinEnvDetected()

    # https://urllib3.readthedocs.org
    # /en/latest/security.html#insecureplatformwarning
    try:
        import urllib3  # pylint: disable=import-outside-toplevel

        urllib3.disable_warnings()
    except (AttributeError, ImportError):
        pass

    # Handle IOError issue with VSCode's Terminal (Windows)
    click_echo_origin = [click.echo, click.secho]

    def _safe_echo(origin, *args, **kwargs):
        try:
            click_echo_origin[origin](*args, **kwargs)
        except IOError:
            (sys.stderr.write if kwargs.get("err") else sys.stdout.write)(
                "%s\n" % (args[0] if args else "")
            )

    click.echo = lambda *args, **kwargs: _safe_echo(0, *args, **kwargs)
    click.secho = lambda *args, **kwargs: _safe_echo(1, *args, **kwargs)


def main(argv=None):
    exit_code = 0
    prev_sys_argv = sys.argv[:]
    if argv:
        assert isinstance(argv, list)
        sys.argv = argv

    try:
        ensure_python3(raise_exception=True)
        configure()
        cli()  # pylint: disable=no-value-for-parameter
    except SystemExit as exc:
        if exc.code and str(exc.code).isdigit():
            exit_code = int(exc.code)
    except Exception as exc:  # pylint: disable=broad-except
        if not isinstance(exc, exception.ReturnErrorCode):
            maintenance.on_superide_exception(exc)
            error_str = f"{exc.__class__.__name__}: "
            if isinstance(exc, exception.SuperIDEException):
                error_str += str(exc)
            else:
                error_str += traceback.format_exc()
                error_str += """
============================================================

An unexpected error occurred. Further steps:

* Verify that you have the latest version of superide using
  `python -m pip install -U super-ide` command

* Report this problem to the developers
  https://gitee.com/SuperIDE/super-ide/issues

============================================================
"""
            click.secho(error_str, fg="red", err=True)
        exit_code = int(str(exc)) if str(exc).isdigit() else 1

    maintenance.on_superide_exit()
    sys.argv = prev_sys_argv
    return exit_code


def debug_gdb_main():
    return main([sys.argv[0], "debug", "--interface", "gdb"] + sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
