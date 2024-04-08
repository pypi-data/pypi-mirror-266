# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""BTTC.

BT testing common utilities.
"""
import atexit

import logging
from mobly.controllers import android_device
from bttc import core
from bttc import errors
from bttc import utils_loader
from bttc.utils import device_factory
from ppadb import client
from typing import TypeAlias


__version__ = '0.0.73'
__author__ = 'John Lee/Yuan Long Luo/Denny Chai'
__credits__ = 'Google Pixel PQM'


GeneralDevice: TypeAlias = android_device.AndroidDevice


def get(
    serial_number: str | None = None,
    required_utility_names: set[str] | None = None,
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False):
  """Retrieves an Android device instance based on the provided serial number.

  Args:
    serial_number: Serial number of the device to retrieve.
        If not provided, automatically selects the first available device.
    required_utility_names: Set of function module names to bind to the
        device.
    init_mbs: If True, initializes the MBS service on the device.
    init_sl4a: If True, initializes the SL4A service on the device.
    init_snippet_uiautomator: If True, initializes the Snippet UiAutomator
        service.
    init_tl4a: If True, initializes the TL4A service.

Returns:
    An initialized Android device instance.

Raises:
    AdbDeviceError: If no devices are found, or multiple devices are found
        without providing a specific serial number.
  """
  if not serial_number:
    adb_client = client.Client(host='localhost', port=5037)
    device_sn_list = [device.serial for device in adb_client.devices()]
    if len(device_sn_list) == 0:
      raise errors.AdbDeviceError('No device found attached!')
    elif len(device_sn_list) > 1:
      raise errors.AdbDeviceError(
          'Serial number is not given and more than one device attached!')

    serial_number = device_sn_list[0]
    logging.debug(
        '`serial_number` is not given and select only '
        'one attached device with serial number=%s...', serial_number)

  func_module_info = utils_loader.get_util_modules()
  required_utility_names = required_utility_names or {}
  not_supported_utility_names = [
      utility_name for utility_name in required_utility_names
      if utility_name not in func_module_info.keys()
  ]
  if not_supported_utility_names:
    raise errors.UnknownUtilityNameError(not_supported_utility_names)

  device = device_factory.get(
      serial_number, init_mbs=init_mbs, init_sl4a=init_sl4a,
      init_snippet_uiautomator=init_snippet_uiautomator,
      init_tl4a=init_tl4a)
  atexit.register(device.services.stop_all)
  for module_name, module_info in func_module_info.items():
    if module_name in required_utility_names or module_info.auto_load:
      module_info.module.bind(device)

  return device


def get_all(
    required_utility_names: set[str] | None = None,
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False):
  """Retrieves instances of all connected Android devices.

  Args:
    required_utility_names: Set of function module names to bind to each
        device.
    init_mbs: If True, initializes the MBS service on each device.
    init_sl4a: If True, initializes the SL4A service on each device.
    init_snippet_uiautomator: If True, initializes the Snippet UiAutomator
        service.
    init_tl4a: If True, initializes the TL4A service.

Returns:
    A dictionary where keys are device serial numbers and values are initialized
    Device instances.
  """
  device_info = {}
  adb_client = client.Client(host='localhost', port=5037)
  for device in adb_client.devices():
    device_info[device.serial] = get(
        device.serial,
        required_utility_names=required_utility_names,
        init_mbs=init_mbs,
        init_sl4a=init_sl4a,
        init_snippet_uiautomator=init_snippet_uiautomator,
        init_tl4a=init_tl4a)

  return device_info


def list_utils(dut: GeneralDevice) -> list[core.UtilBase]:
  """Gets loaded utilities from the given DUT.

  Args:
    dut: Device to search loaded utilities.

  Returns:
    List of loaded utilities.
  """
  loaded_utils = []
  for field_name, field_obj in dut.__dict__.items():
    if isinstance(field_obj, core.UtilBase):
      print(f'Loaded "{field_name}": {field_obj.DESCRIPTION}')
      loaded_utils.append(field_obj)

  return loaded_utils
