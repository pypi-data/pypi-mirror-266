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

from pathlib import Path

from superide import __version__, app, fs, util
from superide.home.rpc.handlers.base import BaseRPCHandler
from superide.project.helpers import is_platformio_project


class AppRPC():
    IGNORE_STORAGE_KEYS = [
        "cid",
        "coreVersion",
        "coreSystype",
        "coreCaller",
        "coreSettings",
        "homeDir",
        "projectsDir",
    ]

    @staticmethod
    def load_state():
        with app.State(
            app.resolve_state_path("core_dir", "homestate.json"), lock=True
        ) as state:
            storage = state.get("storage", {})

            # base data
            caller_id = app.get_session_var("caller_id")
            storage["cid"] = app.get_cid()
            storage["coreVersion"] = __version__
            storage["coreSystype"] = util.get_systype()
            storage["coreCaller"] = str(caller_id).lower() if caller_id else None
            storage["coreSettings"] = {
                name: {
                    "description": data["description"],
                    "default_value": data["value"],
                    "value": app.get_setting(name),
                }
                for name, data in app.DEFAULT_SETTINGS.items()
            }

            storage["homeDir"] = fs.expanduser("~")
            storage["projectsDir"] = storage["coreSettings"]["projects_dir"]["value"]

            # skip non-existing recent projects
            storage["recentProjects"] = list(
                set(
                    str(Path(p).resolve())
                    for p in storage.get("recentProjects", [])
                    if is_platformio_project(p)
                )
            )

            state["storage"] = storage
            state.modified = False  # skip saving extra fields
            return state.as_dict()

    @staticmethod
    def get_state():
        return AppRPC.load_state()

    @staticmethod
    def save_state(state):
        with app.State(
            app.resolve_state_path("core_dir", "homestate.json"), lock=True
        ) as s:
            s.clear()
            s.update(state)
            storage = s.get("storage", {})
            for k in AppRPC.IGNORE_STORAGE_KEYS:
                if k in storage:
                    del storage[k]
        return True
