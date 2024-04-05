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

# from ajsonrpc.core import JSONRPC20DispatchException

# from superide.compat import aio_to_thread
from superide.home.rpc.handlers.base import BaseRPCHandler
from superide.registry.client import RegistryClient


class RegistryRPC():
    @staticmethod
    async def call_client(method, *args, **kwargs):
        try:
            client = RegistryClient()
            return await aio_to_thread(getattr(client, method), *args, **kwargs)
        except Exception as exc:  # pylint: disable=bare-except
            raise JSONRPC20DispatchException(
                code=5000, message="Registry Call Error", data=str(exc)
            ) from exc
