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
import os
import click
import subprocess


from superide import app, exception, fs, util
from superide.project.config import ProjectConfig
from superide.registry.client import RegistryClient

@click.command("pull", short_help="pull environment image")
@click.option("-e", "--environment", 
              multiple=False, 
              help="existing environment image")
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, writable=True),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("-s", "--silent", is_flag=True)
@click.pass_context
def cli(    
    ctx,
    environment,
    project_dir,
    project_conf,
    silent,
):
    # 指明下载环境镜像
    if environment:
        install_environment(environment)
    else:# 将当前项目依赖的环境镜像下载
        install_project_dependencies(
            options=dict(
                project_dir=project_dir,
            )
        )
    click.secho(
        f"Pull environment image successfully!",
        fg="green",
    )
    return True   

def install_project_dependencies(options):
    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        for env in config.envs():
            if not options.get("silent"):
                click.echo("Resolving %s dependencies..." % click.style(env, fg="cyan"))
            name=config.get(f"env:"+env,"env_image")
            already_up_to_date = not install_environment(name, options)
            if not options.get("silent") and already_up_to_date:
                click.secho("Already up-to-date.", fg="green")

def install_environment(env, options=None):
    options = options or {}
    installed_conds = [] # docker image list depends on SuperIDE.ini 

    if not any(installed_conds):
        client = RegistryClient()
        installed_conds.append(
            client.get_package(env)
        )
    return any(installed_conds)

# 
# Developer Verify Tests
# 
import click
from click.testing import CliRunner

def test_pull():
    runner = CliRunner()
    result = runner.invoke(cli, ['-e ubuntu'])
    assert result.exit_code == 0

if __name__ == '__main__':
    test_pull()