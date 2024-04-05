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

from superide.exception import SuperIDEException, UserSideException


class ProjectError(SuperIDEException):
    pass


class NotPlatformIOProjectError(ProjectError, UserSideException):
    MESSAGE = (
        "Not a superide project. `SuperIDE.ini` file has not been "
        "found in current working directory ({0}). To initialize new project "
        "please use `superide project init` command"
    )


class InvalidProjectConfError(ProjectError, UserSideException):
    MESSAGE = "Invalid '{0}' (project configuration file): '{1}'"


class UndefinedEnvPlatformError(ProjectError, UserSideException):
    MESSAGE = "Please specify platform for '{0}' environment"


class ProjectEnvsNotAvailableError(ProjectError, UserSideException):
    MESSAGE = "Please setup environments in `SuperIDE.ini` file"


class UnknownEnvNamesError(ProjectError, UserSideException):
    MESSAGE = "Unknown environment names '{0}'. Valid names are '{1}'"


class InvalidEnvNameError(ProjectError, UserSideException):
    MESSAGE = (
        "Invalid environment name '{0}'. The name can contain "
        "alphanumeric, underscore, and hyphen characters (a-z, 0-9, -, _)"
    )


class ProjectOptionValueError(ProjectError, UserSideException):
    MESSAGE = "{0} for option `{1}`{2}in section [{3}]"
