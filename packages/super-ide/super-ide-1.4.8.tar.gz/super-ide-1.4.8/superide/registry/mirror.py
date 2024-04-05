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

import json
from urllib.parse import urlparse

from superide import __registry_mirror_hosts__
from superide.cache import ContentCache
from superide.http import HTTPClient
from superide.registry.client import RegistryClient


class RegistryFileMirrorIterator:
    HTTP_CLIENT_INSTANCES = {}

    def __init__(self, download_url):
        self.download_url = download_url
        self._url_parts = urlparse(download_url)
        self._mirror = "%s://%s" % (self._url_parts.scheme, self._url_parts.netloc)
        self._visited_mirrors = []

    def __iter__(self):  # pylint: disable=non-iterator-returned
        return self

    def __next__(self):
        cache_key = ContentCache.key_from_args(
            "head", self.download_url, self._visited_mirrors
        )
        with ContentCache("http") as cc:
            result = cc.get(cache_key)
            if result is not None:
                try:
                    headers = json.loads(result)
                    return (
                        headers["Location"],
                        headers["X-PIO-Content-SHA256"],
                    )
                except (ValueError, KeyError):
                    pass

            http = self.get_http_client()
            response = http.send_request(
                "head",
                self._url_parts.path,
                allow_redirects=False,
                params=dict(bypass=",".join(self._visited_mirrors))
                if self._visited_mirrors
                else None,
                x_with_authorization=RegistryClient.allowed_private_packages(),
            )
            stop_conditions = [
                response.status_code not in (302, 307),
                not response.headers.get("Location"),
                not response.headers.get("X-PIO-Mirror"),
                response.headers.get("X-PIO-Mirror") in self._visited_mirrors,
            ]
            if any(stop_conditions):
                raise StopIteration
            self._visited_mirrors.append(response.headers.get("X-PIO-Mirror"))
            cc.set(
                cache_key,
                json.dumps(
                    {
                        "Location": response.headers.get("Location"),
                        "X-PIO-Content-SHA256": response.headers.get(
                            "X-PIO-Content-SHA256"
                        ),
                    }
                ),
                "1h",
            )
            return (
                response.headers.get("Location"),
                response.headers.get("X-PIO-Content-SHA256"),
            )

    def get_http_client(self):
        if self._mirror not in RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES:
            endpoints = [self._mirror]
            for host in __registry_mirror_hosts__:
                endpoint = f"https://dl.{host}"
                if endpoint not in endpoints:
                    endpoints.append(endpoint)
            RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror] = HTTPClient(
                endpoints
            )
        return RegistryFileMirrorIterator.HTTP_CLIENT_INSTANCES[self._mirror]
