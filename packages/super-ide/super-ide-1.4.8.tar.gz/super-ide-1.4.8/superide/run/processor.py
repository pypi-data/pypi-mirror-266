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

# from superide.package.commands.install import install_project_env_dependencies
# from superide.platform.factory import PlatformFactory
from superide.project.exception import UndefinedEnvPlatformError
from superide.run.helpers import KNOWN_ALLCLEAN_TARGETS
from superide.toolchain.toolchain import Toolchain
import subprocess
import click,re,sys
from superide import fs, proc

# from superide.test.runners.base import CTX_META_TEST_RUNNING_NAME
CTX_META_TEST_RUNNING_NAME = __name__ + ".test_running_name"
# pylint: disable=too-many-instance-attributes

class EnvironmentProcessor:
    LINE_ERROR_RE = re.compile(r"(^|\s+)Error:?\s+", re.I)
    def __init__(  # pylint: disable=too-many-arguments
        self,
        cmd_ctx,
        name,
        config,
        targets,
        upload_port,
        jobs,
        program_args,
        silent,
        verbose,
        project_dir,
        command
    ):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.config = config
        self.targets = targets
        self.upload_port = upload_port
        self.jobs = jobs
        self.program_args = program_args
        self.silent = silent
        self.verbose = verbose
        self.project_dir = project_dir
        self.command = " ".join(command).strip()
        self.options = config.items(env=name, as_dict=True)

    def get_build_variables(self):
        variables = dict(
            pioenv=self.name,
            project_config=self.config.path,
            program_args=self.program_args,
        )

        if CTX_META_TEST_RUNNING_NAME in self.cmd_ctx.meta:
            variables["piotest_running_name"] = self.cmd_ctx.meta[
                CTX_META_TEST_RUNNING_NAME
            ]

        if self.upload_port:
            # override upload port with a custom from CLI
            variables["upload_port"] = self.upload_port
        return variables

    def process(self):
        # if "platform" not in self.options:
        #     raise UndefinedEnvPlatformError(self.name)

        build_vars = self.get_build_variables()
        is_clean = set(KNOWN_ALLCLEAN_TARGETS) & set(self.targets)
        build_targets = [t for t in self.targets if t not in KNOWN_ALLCLEAN_TARGETS]

        # pre-clean
        if is_clean:
            # result = PlatformFactory.from_env(
            #     self.name, targets=self.targets, autoinstall=True
            # ).run(build_vars, self.targets, self.silent, self.verbose, self.jobs)
            if not build_targets:
                return 1
                return result["returncode"] == 0

        projectdir=self.project_dir
        image_name=self.name
        if self.command:
            if self.command == 'build':
                command=Toolchain(image_name,projectdir).build()
            elif self.command == 'check':
                command=Toolchain(image_name,projectdir).check()
            elif self.command == 'run':
                command=Toolchain(image_name,projectdir).run()
            else:
                command = Toolchain(image_name,projectdir).container_command(self.command)
            try:
                result = self.CommandRun(command)
            except:
                print("command run failed")
                return False;
        else:
            build_command=Toolchain(image_name,projectdir).build()
            check_command=Toolchain(image_name,projectdir).check()
            run_command=Toolchain(image_name,projectdir).run()
            commands= [build_command, check_command, run_command]
            try:
                for comand in commands:
                    result = self.CommandRun(comand)
            except:
                return False;
        
        
        # (self.name, targets=build_targets, autoinstall=True).run
        return True
    
    def CommandRun(self,command):
        def _write_and_flush(stream, data):
            try:
                stream.write(data)
                stream.flush()
            except IOError:
                pass

        return proc.exec_command(
                command.split(),
                stdout=proc.BuildAsyncPipe(
                    line_callback=self._on_stdout_line,
                    data_callback=lambda data: None
                    # if self.silent
                    # else _write_and_flush(sys.stdout, data),
                ),
                stderr=proc.BuildAsyncPipe(
                    line_callback=self._on_stderr_line,
                    data_callback=lambda data: _write_and_flush(sys.stderr, data),
                ),
            )

    def _echo_line(self, line, level):
        assert 1 <= level <= 3
        # if self.silent and (level < 2 or not line):
        #     return
        fg = (None, "yellow", "red")[level - 1]
        if level == 1 and "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg, err=level > 1, nl=False)

    def _on_stdout_line(self, line):
        if "`buildprog' is up to date." in line:
            return
        self._echo_line(line.strip()+'\n', level=1)

    def _on_stderr_line(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        self._echo_line(line.strip()+'\n', level=3 if is_error else 2)

        a_pos = line.find("fatal error:")
        b_pos = line.rfind(": No such file or directory")
        if a_pos == -1 or b_pos == -1:
            return
        self._echo_missed_dependency(line[a_pos + 12 : b_pos].strip())

        # result = {"out": None, "err": None, "returncode": None}
        # try:
        #     res = subprocess.run(["docker", "run","-it","--rm", "-v", projectdir+":"+projectdir, dockername ]+(command+projectdir).split(), 
        #                           text=True)
        #     if res.stdout:
        #         click.echo(res.stdout)
        #     if res.stderr:
        #         click.echo(f"Docker Pull Error:\n{res.stderr}")
        #     else:
        #         click.echo(f"Docker Pull failed with return code: {res.returncode}")
        #     result["returncode"]=res.returncode
        # except Exception as e:
        #     click.echo(f"Error executing the command: {e}")
        # return res

        