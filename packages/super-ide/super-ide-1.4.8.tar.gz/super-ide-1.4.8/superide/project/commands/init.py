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

# pylint: disable=line-too-long,too-many-arguments,too-many-locals


import json
import os
import shutil

    
import click

from superide import __configfile__
from superide import fs
from superide.registry.cli import install_project_dependencies
# from superide.package.manager.platform import PlatformPackageManager
# from superide.platform.exception import UnknownBoard
# from superide.platform.factory import PlatformFactory
from superide.project.config import ProjectConfig
from superide.project.exception import UndefinedEnvPlatformError
from superide.project.helpers import is_platformio_project
# from superide.project.integration.generator import ProjectGenerator
from superide.project.options import ProjectOptions
from superide.project.vcsclient import VCSClientFactory
from superide.toolchain.toolchain import Toolchain

@click.command("init", short_help="Initialize a project or update existing")
@click.option(
    "--project-dir",
    "-d",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
)
@click.option(
    "--env_image", "-i", help="Development environment container image name")
@click.option("-e", "--environment", help="Update existing environment")
@click.option(
    "-O",
    "--project-option",
    "project_options",
    multiple=True,
    help="A `name=value` pair",
)
@click.option("--sample-code", default="")
@click.option("--no-install-dependencies", is_flag=True)
@click.option("--env-prefix", default="")
@click.option("-s", "--silent", is_flag=True)
def project_init_cmd(
    project_dir,
    env_image,
    environment,
    project_options,
    sample_code,
    no_install_dependencies,
    env_prefix,
    silent,
):
    # 用于判断当前目录或project_dir指定的目录下有没有配置文件即__configfile__所代表的ini文件
    is_new_project = not is_platformio_project(project_dir)
    if is_new_project:
        if not silent:
            print_header(project_dir)
        # 从容器镜像拷贝示例项目
        Toolchain(env_image, project_dir).init_project()

    with fs.cd(project_dir):
        if environment:
            # 在配置文件添加[env:ENV_NAME]及key=value
            update_project_env(environment, project_options)

        config = ProjectConfig.get_instance(os.path.join(project_dir, __configfile__))

        # 检查拉取开发环境容器镜像
        if not no_install_dependencies and (environment):
            for env in config.envs():
                env_image = config.get(f"env:{env}", "env_image")
                if env_image:
                    Toolchain(env_image, project_dir).check_image()       

        if is_new_project:
            init_cvs_ignore()

    if not silent:
        print_footer(is_new_project)


def print_header(project_dir):
    click.echo("The following files/directories have been created in ", nl=False)
    try:
        click.secho(project_dir, fg="cyan")
    except UnicodeEncodeError:
        click.secho(json.dumps(project_dir), fg="cyan")
    click.echo("%s - Put project header files here" % click.style("include", fg="cyan"))
    click.echo(
        "%s - Put project specific (private) libraries here"
        % click.style("lib", fg="cyan")
    )
    click.echo("%s - Put project source files here" % click.style("src", fg="cyan"))
    click.echo(
        "%s - Project Configuration File" % click.style(__configfile__, fg="cyan")
    )


def print_footer(is_new_project):
    action = "initialized" if is_new_project else "updated"
    return click.secho(
        f"Project has been successfully {action}!",
        fg="green",
    )


def init_cvs_ignore():
    conf_path = ".gitignore"
    if os.path.isfile(conf_path):
        return
    with open(conf_path, mode="w", encoding="utf8") as fp:
        fp.write(".side\n")

def update_project_env(environment, extra_project_options=None):
    if not extra_project_options:
        return
    env_section = "env:%s" % environment
    # 保持与platformio兼容
    option_to_sections = {"platformio": [], env_section: []}
    for item in extra_project_options:
        assert "=" in item
        name, value = item.split("=", 1)
        name = name.strip()
        destination = env_section
        for option in ProjectOptions.values():
            if option.scope in option_to_sections and option.name == name:
                destination = option.scope
                break
        option_to_sections[destination].append((name, value.strip()))

    config = ProjectConfig(
        __configfile__, parse_extra=False, expand_interpolations=False
    )
    for section, options in option_to_sections.items():
        if not options:
            continue
        if not config.has_section(section):
            config.add_section(section)
        for name, value in options:
            config.set(section, name, value)

    config.save()

