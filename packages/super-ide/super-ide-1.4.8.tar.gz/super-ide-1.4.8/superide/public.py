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

# pylint: disable=unused-import

# from superide.device.list.util import list_logical_devices, list_serial_ports
# from superide.device.monitor.filters.base import DeviceMonitorFilterBase
from superide.fs import to_unix_path
# from superide.platform.base import PlatformBase
from superide.project.config import ProjectConfig
from superide.project.helpers import get_project_watch_lib_dirs, load_build_metadata
from superide.project.options import get_config_options_schema
# from superide.test.result import TestCase, TestCaseSource, TestStatus
# from superide.test.runners.base import TestRunnerBase
# from superide.test.runners.doctest import DoctestTestCaseParser
# from superide.test.runners.googletest import GoogletestTestRunner
# from superide.test.runners.unity import UnityTestRunner
from superide.util import get_systype
