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

from setuptools import find_packages, setup

from superide import (
    __author__,
    __description__,
    __email__,
    __license__,
    __title__,
    __url__,
    __version__,
)

py_37 = "python_version == '3.7'"
py_below_37 = "python_version < '3.7'"
py_gte_37 = "python_version >= '3.7'"
py_gte_38 = "python_version >= '3.8'"

minimal_requirements = [
    "bottle==0.12.*",
    "click==8.0.4; " + py_below_37,
    "click==8.1.*; " + py_gte_37,
    "colorama",
    "marshmallow==3.14.1; " + py_below_37,
    "marshmallow==3.19.*; " + py_gte_37,
    "pyelftools==0.29",
    "pyserial==3.5.*",  # keep in sync "device/monitor/terminal.py"
    "requests==2.*",
    "semantic_version==2.10.*",
    "tabulate==0.*",
]

home_requirements = [
    "Flask==3.0.0" ,
    "Flask-SocketIO==5.3.6",
    "GitPython>=3.1.40",
]

# issue 4614: urllib3 v2.0 only supports OpenSSL 1.1.1+
try:
    import ssl

    if ssl.OPENSSL_VERSION.startswith("OpenSSL ") and ssl.OPENSSL_VERSION_INFO < (
        1,
        1,
        1,
    ):
        minimal_requirements.append("urllib3<2")
except ImportError:
    pass


setup(
    name=__title__,
    version=__version__,
    description=__description__,
    long_description=open("README.rst").read(),
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    install_requires=minimal_requirements + home_requirements,
    python_requires=">=3.6",
    packages=find_packages(include=["superide", "superide.*"]),
    include_package_data=True,
    package_data={
        "superide": [
            "assets/system/99-superide-udev.rules",
            "home/static/*",  
            "home/static/assets/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "si = superide.__main__:main",
            "superide = superide.__main__:main",
            "super-ide = superide.__main__:main",
            "sidebuggdb = superide.__main__:debug_gdb_main",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Compilers",
    ],
    keywords=[
        "iot",
        "embedded",
        "arduino",
        "mbed",
        "esp8266",
        "esp32",
        "fpga",
        "firmware",
        "continuous-integration",
        "cloud-ide",
        "avr",
        "arm",
        "ide",
        "unit-testing",
        "hardware",
        "verilog",
        "microcontroller",
        "debug",
    ],
)
