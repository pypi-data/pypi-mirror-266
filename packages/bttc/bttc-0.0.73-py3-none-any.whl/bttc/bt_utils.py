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

"""Utility to support common BT operations/methods."""
import datetime
from functools import partial
import logging
import time

from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb
from bttc import bt_data
from bttc import common_data
from bttc import constants
from bttc import core
from bttc.utils import device_factory
from bttc.utils import log_parser

import shlex
import re
from typing import Any, Callable, Sequence, TypeAlias, Union


BINDING_KEYWORD = 'bt'
AUTO_LOAD = True
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice
BT_BONDED_STATE: TypeAlias = constants.BluetoothBondedState
BT_PAIRED_DEVICE: TypeAlias = bt_data.PairedDeviceInfo
BT_BONDED_DEVICE: TypeAlias = bt_data.BondedDeviceInfo

# Logcat message timestamp format
_DATETIME_FMT = constants.LOGCAT_DATETIME_FMT

# Pattern to match message of logcat service.
_LOGCAT_MSG_PATTERN = constants.LOGTCAT_MSG_PATTERN


class BTModule(core.UtilBase):
  """BT module to hold BT related functions define in this module."""

  NAME = BINDING_KEYWORD
  DESCRIPTION = (
      'Utility to support Bluetooth base operations such as turn on/off '
      'Bluetooth.')

  def __init__(self, ad: ANDROID_DEVICE):
    super().__init__(ad)
    self._bind(crash_since)
    self._bind(dump_bluetooth_manager)
    self._bind(enable_snoop_log)
    self._bind(enable_gd_log_verbose)
    self._bind(get_bluetooth_mac_address)
    self._bind(get_bonded_devices)
    self._bind(get_device_mac_by_name)
    self._bind(get_connected_ble_devices)
    self._bind(get_current_le_audio_active_group_id)
    self._bind(is_le_audio_device_connected)
    self._bind(is_bluetooth_enabled, 'is_enabled')
    self._bind(list_paired_devices)
    self._bind(unbond_device)
    self.shell = safe_adb_shell(ad)
    self.enable = partial(toggle_bluetooth, ad=ad, enabled=True)
    self.disable = partial(toggle_bluetooth, ad=ad, enabled=False)

  @property
  def enabled(self):
    return self.is_enabled()

  @property
  def bonded_devices(self):
    return {d.name: d for d in self.get_bonded_devices()}

  @property
  def bonded_device_names(self):
    return [device.name for device in self.bonded_devices]

  @property
  def paired_devices(self):
    return {
        d.name: d
        for d in self.list_paired_devices(only_name=False)}

  @property
  def paired_device_names(self):
    return self.list_paired_devices()


def bind(
    ad: Union[ANDROID_DEVICE, str],
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False) -> ANDROID_DEVICE:
  """Binds the input device with functions defined in module `bt_utils`.

  Sample Usage:
  ```python
  >>> from bttc import bt_utils
  >>> ad = bt_utils.bind('35121FDJG0005P', init_mbs=True, init_sl4a=True)
  >>> ad.bt.is_bluetooth_enabled()
  True
  >>> ad.bt.list_paired_devices()
  ['Galaxy Buds2 Pro', 'Galaxy Buds2 Pro']
  ```

  Args:
    ad: If string is given, it stands for serial of device. Otherwise, it should
        be the Android device object.
    init_mbs: True to initialize the MBS service of given device.
    init_sl4a: True to initialize the SL4A service of given device.

  Returns:
    The device with binded functions defined in `bt_utils`.
  """
  device = device_factory.get(
      ad, init_mbs=init_mbs,
      init_sl4a=init_sl4a,
      init_snippet_uiautomator=init_snippet_uiautomator,
      init_tl4a=init_tl4a)
  device.load_config({BINDING_KEYWORD: BTModule(device)})

  return device


def crash_since(
    device: android_device.AndroidDevice,
    start_time: str | None = None) -> common_data.CrashInfo:
  """Collects crash timestamp.

  Usage example:
  ```python
  >>> import bttc
  >>> dut = bttc.get('36121FDJG000GR')
  >>> device_time = dut.gm.device_time
  >>> dut.bt.crash_since(device_time)  # We actually have two crash occurred before `device_time`  # noqa: E501
  CrashInfo(total_num_crash=2, collected_crash_times=[])
  >>> dut.bt.crash_since()  # Collect all crash time
  CrashInfo(total_num_crash=2, collected_crash_times=['02-07 08:55:35.085', '02-07 09:08:12.584'])
  >>> dut.bt.crash_since('02-07 08:56:35.085')  # Collect crash timestamp after  '02-07 08:56:35.085'
  CrashInfo(total_num_crash=2, collected_crash_times=['02-07 09:08:12.584'])
  ```

  Args:
    device: Adb like device.
    start_time: start time in string format of `_DATETIME_FMT`. If not give, all
      crash timestamp will be collected.

  Returns:
    Crash information including total crash count and collected crash timestamp.
  """
  start_datetime_obj = None
  try:
    if start_time:
      start_datetime_obj = datetime.datetime.strptime(start_time, _DATETIME_FMT)
  except ValueError as ex:
    logging.error('Invalid time format = "%s"!', start_time)
    raise ex

  crash_time_info = common_data.CrashInfo()
  bluetooth_crash_header_pattern = re.compile(
      r'Bluetooth crashed (?P<num_crash>\d+) time')

  # The interested parsing content will look lik:
  # usky:/ # dumpsys bluetooth_manager | grep -A 20 "Bluetooth crashed"
  # Bluetooth crashed 2 time
  # 02-07 08:55:35.085
  # 02-07 10:35:04.011
  #
  bt_manager_messages = dump_bluetooth_manager(device).split('\n')
  for i, line in enumerate(bt_manager_messages):
    matcher = bluetooth_crash_header_pattern.match(line)
    if matcher:
      crash_num = int(matcher.group('num_crash'))
      logging.info('Total %s crash being detected!', crash_num)
      crash_time_info.total_num_crash = crash_num
      for line_num in range(i+1, len(bt_manager_messages)):
        crash_time = bt_manager_messages[line_num].strip()
        if not crash_time:
          break

        crash_datetime_obj = datetime.datetime.strptime(
            crash_time, _DATETIME_FMT)
        if (
            not start_datetime_obj or
            crash_datetime_obj >= start_datetime_obj):
          crash_time_info.collected_crash_times.append(crash_time)

    if crash_time_info.total_num_crash >= 0:
      break

  return crash_time_info


def dump_bluetooth_manager(ad: android_device.AndroidDevice,
                           args: Sequence[str] = ()) -> str:
  """Dumps Bluetooth Manager log for the device.

  Args:
    args: Other arguments to be used in the dump command.

  Returns:
    Output of the dump command.
  """
  return ad.adb.shell(
      ('dumpsys', 'bluetooth_manager', *args)).decode()


def enable_snoop_log(ad: android_device.AndroidDevice) -> bool:
  """Enables Snoop log."""
  property_name = 'persist.bluetooth.btsnooplogmode'
  ad.log.info('Enabling Bluetooth Snoop log...')
  ad.adb.shell(f'setprop {property_name} full')
  property_setting = ad.adb.shell(
      f'getprop {property_name}').decode().strip()
  if property_setting == 'full':
    ad.log.info('Successfully enabled Bluetooth Snoop Log.')
    return True

  ad.log.warning(
      'Failed to enable Bluetooth Snoop Log with '
      'unexpected current setting="%s"', property_setting)
  return False


def enable_gd_log_verbose(ad: android_device.AndroidDevice) -> bool:
  """Enables bluetooth Gabeldorsche verbose log."""
  if int(ad.build_info['build_version_sdk']) >= 33:
    ad.log.info('Enabling Bluetooth GD verbose logging...')
    ad.adb.shell('device_config set_sync_disabled_for_tests persistent')
    ad.adb.shell('device_config put bluetooth '
                 'INIT_logging_debug_enabled_for_all true')
    out = ad.adb.shell(
        'device_config get bluetooth '
        'INIT_logging_debug_enabled_for_all').decode()
    if 'true' in out:
      ad.log.info('Successfully enabled Bluetooth GD verbose logging.')
      return True
  else:
    ad.log.warning(
        'Not TM or above build. Skip the enable GD verbose logging.')

  return False


def get_bluetooth_mac_address(ad: android_device.AndroidDevice) -> str:
    """Gets Bluetooth mac address of an AndroidDevice."""
    ad.log.info('Getting Bluetooth mac address.')
    mac_address = ad.adb.shell(
            'settings get secure bluetooth_address').decode('utf8').strip()
    ad.log.info('Bluetooth mac address: %s', mac_address)
    return mac_address


def get_bonded_devices(
    ad: android_device.AndroidDevice) -> list[BT_BONDED_DEVICE]:
  """Retrieves information about bonded Bluetooth devices.

  Args:
    ad: The Android device object.

  Returns:
    A list of bonded device information objects.
  """
  return log_parser.parse_bonded_device_info(
      dump_bluetooth_manager(ad))


def get_connected_ble_devices(
    ad: android_device.AndroidDevice) -> list[dict[str, Any]]:
  """Returns devices connected through bluetooth LE.

  Returns:
       List of conncted le devices info.
  """
  return ad.sl4a.bluetoothGetConnectedLeDevices(
      constants.BluetoothProfile.GATT)


def get_current_le_audio_active_group_id(
    ad: android_device.AndroidDevice) -> int:
    """Gets current LE Audio active group ID.

    Returns:
      LE Audio group ID.
    """
    dump = dump_bluetooth_manager(
        ad, ('|', 'grep', '"currentlyActiveGroupId"', '||', 'echo', ' '))
    result = re.search(r'currentlyActiveGroupId: (.*)', dump)
    if result and result.group(1) != '-1':
      return int(result.group(1))
    ad.log.info('No LE Audio group active.')
    return -1


def get_device_mac_by_name(
    ad: android_device.AndroidDevice, bt_name: str) -> list[str]:
  """Retrieves the MAC address(es) of a paired Bluetooth device by its name.

  Args:
    ad: The Android device object.
    bt_name: The name of the Bluetooth device.

  Returns:
    A list of MAC addresses associated with the given device name.
    The list might contain multiple addresses if the device supports
    multiple Bluetooth profiles.

  Raises:
    Exception: If no paired device is found with the specified name.
  """

  paired_devices = ad.mbs.btGetPairedDevices()
  mac_address_list = []

  for device_info in paired_devices:
    if device_info['Name'] == bt_name:
      mac_address_list.append(device_info['Address'])

  if not mac_address_list:
    raise Exception(f'BT name={bt_name} does not exist!')

  return mac_address_list


def is_bluetooth_enabled(ad: android_device.AndroidDevice) -> bool:
  """Checks if Bluetooth is enabled on an Android device.

  Args:
    ad: The Android device object.

  Returns:
    True if Bluetooth is enabled, False otherwise.
  """
  return 'enabled: true' in dump_bluetooth_manager(
      ad, ('|', 'grep', '-A1', '"Bluetooth Status"', '||', 'echo', ' '))


def is_le_audio_device_connected(
    ad: android_device.AndroidDevice, mac_address: str) -> bool:
  """Checks if the LE Audio device is connected.

  Args:
    mac_address: Bluetooth MAC address of the LE Audio device.

  Returns:
    True iff the LE Audio device is connected.
  """
  # NOMUTANTS -- Grep keyword in dump.
  dump = dump_bluetooth_manager(ad, (
      '|', 'grep', '-B5',
      f'"group lead: XX:XX:XX:XX:{mac_address[-5:].upper()}"', '||', 'echo',
      ' '))
  return 'isConnected: true' in dump


def list_paired_devices(
    ad: android_device.AndroidDevice,
    only_name: bool = True) -> list[BT_PAIRED_DEVICE]:
  """Retrieves information about paired Bluetooth devices.

  Args:
    ad: The Android device object.
    only_name: If True, returns a list of paired device names only.
        If False, returns detailed device information. Defaults to True.

  Returns:
    A list of paired device names (if `only_name` is True) or a list of
    dictionaries containing detailed device information.
  """
  paired_devices = ad.mbs.btGetPairedDevices()
  if only_name:
    return list(
        map(lambda paired_info: paired_info['Name'], paired_devices))

  return [
      bt_data.PairedDeviceInfo.from_dict(pair_info_dict)
      for pair_info_dict in paired_devices]


def safe_adb_shell(
    device: android_device.AndroidDevice,
    use_shlex_split: bool = True,
    timeout: float | None = None) -> Callable[[str], tuple[str, str, int]]:
  """Gets safe adb shell executor.

  Below is demo of this function:
  ```python
  >>> from bttc import bt_utils
  >>> from mobly.controllers import android_device
  >>> phone = android_device.create([{'serial': '07311JECB08252'}])[0]
  >>> safe_adb = bt_utils.safe_adb_shell(phone)
  >>> stdout, stderr, rt = safe_adb('getprop ro.build.version.sdk')
  >>> stdout  # My phone is of SDK 30.
  '30\n'
  ```

  Args:
    device: Adb like device.
    use_shlex_split: Leverage shlex.split iff True.
    timeout: float, the number of seconds to wait before timing out. If not
      specified, no timeout takes effect.

  Returns:
    Safe callable adb object.
  """

  def _adb_wrapper(command: str) -> tuple[str, str, int]:
    try:
      command = shlex.split(command) if use_shlex_split else command
      command_output = device.adb.shell(command, timeout=timeout).decode()
      return (command_output, '', 0)
    except adb.AdbError as err:
      return (err.stdout.decode(encoding='utf-8', errors='strict'),
              err.stderr.decode(encoding='utf-8',
                                errors='strict'), err.ret_code)
    except adb.AdbTimeoutError as err:
      device.log.warning('Timeout in executing command: %s', command)
      return ('', str(err), -1)

  return _adb_wrapper


def toggle_bluetooth(
    ad: android_device.AndroidDevice, enabled: bool = True) -> None:
  """Enables or disables Bluetooth on an Android device.

  Args:
    ad: The Android device object.
    enabled: True to enable Bluetooth, False to disable it.

  RuntimeError: If Bluetooth could not be toggled successfully. The error
      message includes the attempted state ('enabled' or 'disabled'),
      return code, and command output for troubleshooting.
  """
  status = 'enable' if enabled else 'disable'
  cmd = f'svc bluetooth {status}'
  stdout, _, ret_code = safe_adb_shell(ad)(cmd)
  stdout = stdout.strip()
  # Expect 'disable: Success' or 'enable: Success'
  if ret_code == 0 and any([
      'Success' in stdout,
      stdout in {
          'Enabling Bluetooth',  # BDS's output
          '',  # SDK version < 33 (b/297539822#comment4)
      }]):
    return

  ad.log.warning(
      'Failed to toggle bluetooth with enabled=%s (rt=%s):\n%s\n',
      enabled, ret_code, stdout)

  raise RuntimeError(
      f'Failed in toggling bluetooth (enabled={enabled}) '
      f'with stdout: "{stdout}"')


def unbond_device(
    ad: android_device.AndroidDevice,
    name_or_mac: str,
    ignore_not_exist: bool = True,
    wait_time_sec: float = 3) -> bool:
  """Unbonds the BT device by its' name or MAC address.

  This operation requires DUT to be initialized with SL4A service.

  Args:
    ad: The Android device object.
    name_or_mac: Name or MAC of BT device to be unbonded.
    ignore_not_exist: True to ignore the case that if the target BT to be
        unbondeddoes not exist.

  Returns:
    True iff the target BT device is unbonded successfully.
  """
  for bt_name, bonded_device_info in ad.bt.bonded_devices.items():
    if name_or_mac in {bt_name, bonded_device_info.mac_addr}:
      ad.sl4a.bluetoothUnbond(bonded_device_info.mac_addr)
      ad.log.debug(
          'Sleep %ss for unbond action to become active...', wait_time_sec)
      time.sleep(wait_time_sec)
      name_or_mac_set = set()
      for bt_name, bonded_device_info in ad.bt.bonded_devices.items():
        name_or_mac_set.add(bt_name)
        name_or_mac_set.add(bonded_device_info.mac_addr)

      return name_or_mac not in name_or_mac_set

  ad.log.warning('Target device=%s does not exist!', name_or_mac)
  return ignore_not_exist
