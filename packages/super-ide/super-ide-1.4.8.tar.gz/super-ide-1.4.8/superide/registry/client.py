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

# pylint: disable=too-many-arguments
import subprocess
from time import time
#from superide import app, fs, proc, telemetry
import sys,click,re
from superide import __registry_mirror_hosts__, fs, proc
# from superide.account.client import AccountClient, AccountError
from superide.http import HTTPClient, HTTPClientError


class RegistryClient(HTTPClient):
    LINE_ERROR_RE = re.compile(r"(^|\s+)Error:?\s+", re.I)
    def __init__(self):
        endpoints = [f"https://api.{host}" for host in __registry_mirror_hosts__]
        super().__init__(endpoints)

    @staticmethod
    def allowed_private_packages():
        private_permissions = set(
            [
                "service.registry.publish-private-tool",
                "service.registry.publish-private-platform",
                "service.registry.publish-private-library",
            ]
        )
        # try:
        #     info = AccountClient().get_account_info() or {}
        #     for item in info.get("packages", []):
        #         if set(item.keys()) & private_permissions:
        #             return True
        # except AccountError:
        #     pass
        return False

    def publish_package(  # pylint: disable=redefined-builtin
        self, owner, type, archive_path, released_at=None, private=False, notify=True
    ):
        with open(archive_path, "rb") as fp:
            return self.fetch_json_data(
                "post",
                "/v3/packages/%s/%s" % (owner, type),
                params={
                    "private": 1 if private else 0,
                    "notify": 1 if notify else 0,
                    "released_at": released_at,
                },
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-PIO-Content-SHA256": fs.calculate_file_hashsum(
                        "sha256", archive_path
                    ),
                },
                data=fp,
                x_with_authorization=True,
            )

    def unpublish_package(  # pylint: disable=redefined-builtin
        self, owner, type, name, version=None, undo=False
    ):
        path = "/v3/packages/%s/%s/%s" % (owner, type, name)
        if version:
            path += "/" + version
        return self.fetch_json_data(
            "delete", path, params={"undo": 1 if undo else 0}, x_with_authorization=True
        )

    def update_resource(self, urn, private):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s" % urn,
            data={"private": int(private)},
            x_with_authorization=True,
        )

    def grant_access_for_resource(self, urn, client, level):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s/access" % urn,
            data={"client": client, "level": level},
            x_with_authorization=True,
        )

    def revoke_access_from_resource(self, urn, client):
        return self.fetch_json_data(
            "delete",
            "/v3/resources/%s/access" % urn,
            data={"client": client},
            x_with_authorization=True,
        )

    def list_resources(self, owner):
        return self.fetch_json_data(
            "get",
            "/v3/resources",
            params={"owner": owner} if owner else None,
            x_cache_valid="1h",
            x_with_authorization=True,
        )

    def list_packages(self, query=None, qualifiers=None, page=None, sort=None):
        search_query = []
        if qualifiers:
            valid_qualifiers = (
                "authors",
                "keywords",
                "frameworks",
                "platforms",
                "headers",
                "ids",
                "names",
                "owners",
                "types",
            )
            assert set(qualifiers.keys()) <= set(valid_qualifiers)
            for name, values in qualifiers.items():
                for value in set(
                    values if isinstance(values, (list, tuple)) else [values]
                ):
                    search_query.append('%s:"%s"' % (name[:-1], value))
        if query:
            search_query.append(query)
        params = dict(query=" ".join(search_query))
        if page:
            params["page"] = int(page)
        if sort:
            params["sort"] = sort
        return self.fetch_json_data(
            "get",
            "/v3/search",
            params=params,
            x_cache_valid="1h",
            x_with_authorization=self.allowed_private_packages(),
        )
    def get_package(self, name, version=None, extra_path=None):
        def _write_and_flush(stream, data):
            try:
                stream.write(data)
                stream.flush()
            except IOError:
                pass

        return proc.exec_command(
                ['docker', 'pull', name],
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
        if line.startswith("scons: "):
            line = line[7:]
        assert 1 <= level <= 3
        # if self.silent and (level < 2 or not line):
        #     return
        fg = (None, "yellow", "red")[level - 1]
        if level == 1 and "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg, err=level > 1, nl=False)

    def _on_stdout_line(self, line):
        if "not be found" in line:
            return
        is_error = True
        self._echo_line(line, level=3 if is_error else 1)

    def _on_stderr_line(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        self._echo_line(line, level=3 if is_error else 2)

        a_pos = line.find("fatal error:")
        b_pos = line.rfind(": No such file or directory")
        if a_pos == -1 or b_pos == -1:
            return
        self._echo_missed_dependency(line[a_pos + 12 : b_pos].strip())

        # try:
        #     result = {"env": name, "duration": time(), "succeeded": True}
        #     ret = subprocess.run(['docker', 'pull', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
        #     if ret.stdout:
        #         print("TEST",ret.stdout)
        #         if "not be found" in ret.stdout:
        #             result["succeeded"]=False
        #         if "Error" in ret.stdout:
        #             result["succeeded"]=False
        #         result["succeeded"] = ret.stdout
        #         result["duration"] = time() - result["duration"]
        #     if ret.stderr:
        #         print(ret.stderr)
        #         result["succeeded"] = f"Docker Pull Error:\n{ret.stderr}"
        #         return None
        #     else:
                
        #         result["succeeded"] = f"Docker Pull failed with return code: {ret.returncode}"
        #         return None
            
        # except Exception as e:
        #     result["succeeded"] = f"Error executing the command: {e}"
        #     return None
        
        # try:
        #     return self.fetch_json_data(
        #         "get",
        #         "/v3/packages/{owner}/{type}/{name}{extra_path}".format(
        #             type=typex,
        #             owner=owner.lower(),
        #             name=name.lower(),
        #             extra_path=extra_path or "",
        #         ),
        #         params=dict(version=version) if version else None,
        #         x_cache_valid="1h",
        #         x_with_authorization=self.allowed_private_packages(),
        #     )
        # except HTTPClientError as exc:
        #     if exc.response is not None and exc.response.status_code == 404:
        #         return None
        #     raise exc
