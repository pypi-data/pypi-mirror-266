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

VERSION = (1, 4, 8)
__version__ = ".".join([str(s) for s in VERSION])

__title__ = "super-ide"
__description__ = (
    "A professional Cross-platform IDE. "
    "Cross-platform IDE and Unified Debugger. "
    "Static Code Analyzer and Remote Unit Testing. "
    "Multi-platform and Multi-architecture Build System. "
    "Firmware File Explorer and Memory Inspection. "
    "IoT, Arduino, CMSIS, ESP-IDF, FreeRTOS, libOpenCM3, mbedOS, Pulp OS, SPL, "
    "STM32Cube, Zephyr RTOS, ARM, AVR, Espressif (ESP8266/ESP32), FPGA, "
    "MCS-51 (8051), MSP430, Nordic (nRF51/nRF52), NXP i.MX RT, PIC32, RISC-V, "
    "STMicroelectronics (STM8/STM32), Teensy"
)
__url__ = "https://mengning.com.cn"

__author__ = "Mengning Software"
__email__ = "contact@mengning.com.cn"

__license__ = "AGPL-3.0 License"
__copyright__ = "Copyright 2014-present Mengning Software"

__accounts_api__ = "https://api.accounts.mengning.com.cn"
__registry_mirror_hosts__ = [
    "registry.mengning.com.cn",
    "registry.nm1.mengning.com.cn",
]
__pioremote_endpoint__ = "ssl:host=remote.mengning.com.cn:port=4413"

__core_packages__ = {
    "tool-scons": "~4.40502.0",
    "tool-cppcheck": "~1.270.0",
    "tool-clangtidy": "~1.150005.0",
    "tool-pvs-studio": "~7.18.0",
}

__check_internet_hosts__ = [
    "185.199.110.153",  # Github.com
    "88.198.170.159",  # mengning.com.cn
    "github.com",
] + __registry_mirror_hosts__

__configfile__ = "SuperIDE.ini"

__container_engine__ = "isula"

