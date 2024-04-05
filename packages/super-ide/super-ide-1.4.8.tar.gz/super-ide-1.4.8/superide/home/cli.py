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

import mimetypes
import socket

import click

from superide.compat import IS_WINDOWS
from superide.home.app import run_server
# from superide.package.manager.core import get_core_package_dir


@click.command("home", short_help="GUI to manage superide")
@click.option("--port", type=int, default=8888, help="HTTP port, default=8888")
@click.option(
    "--host",
    default="127.0.0.1",
    help=(
        "HTTP host, default=127.0.0.1. You can open SI Home for inbound "
        "connections with --host=0.0.0.0"
    ),
)
@click.option("--no-open", is_flag=True)
@click.option(
    "--shutdown-timeout",
    default=0,
    type=int,
    help=(
        "Automatically shutdown server on timeout (in seconds) when no clients "
        "are connected. Default is 0 which means never auto shutdown"
    ),
)
@click.option(
    "--session-id",
    help=(
        "A unique session identifier to keep SI Home isolated from other instances "
        "and protect from 3rd party access"
    ),
)
def cli(port, host, no_open, shutdown_timeout, session_id):
    # Ensure SI Home mimetypes are known
    mimetypes.add_type("text/html", ".html")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("application/javascript", ".js")

    home_url = "http://%s:%d%s" % (
        host,
        port,
        ("/session/%s/" % session_id) if session_id else "/",
    )
    click.echo(
        "\n".join(
            [
                "",
                "  ___I_",
                " /\\-_--\\   Superide Home",
                "/  \\_-__\\",
                "|[]| [] |  %s" % home_url,
                "|__|____|__%s" % ("_" * len(home_url)),
            ]
        )
    )
    click.echo("")
    click.echo("SuperIDE Home has been started.")
    click.echo("Open SuperIDE Home in your browser by this URL => %s" % home_url)

    if is_port_used(host, port):
        click.secho(
            "Superide Home server is already started in another process.", fg="yellow"
        )
        if not no_open:
            click.launch(home_url)
        return

    run_server(
        host=host,
        port=port,
        no_open=no_open,
        shutdown_timeout=shutdown_timeout,
        home_url=home_url,
    )


def is_port_used(host, port):
    socket.setdefaulttimeout(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if IS_WINDOWS:
        try:
            s.bind((host, port))
            s.close()
            return False
        except (OSError, socket.error):
            pass
    else:
        try:
            s.connect((host, port))
            s.close()
        except socket.error:
            return False

    return True
