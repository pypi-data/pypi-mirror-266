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


from dataclasses import fields
from typing import Sequence
from bttc import bt_data
from bttc import constants
from bttc import errors
from bttc import ble_data
import re


BondedDeviceInfo = bt_data.BondedDeviceInfo
LeAudioServiceInfo = ble_data.LeAudioService
ActiveGroupInfo = ble_data.ActiveGroupInfo
GroupInfo = ble_data.GroupInfo
DeviceInfo = ble_data.DeviceInfo
StateMachineLog = ble_data.StateMachineLog
LeAudioStateMachine = ble_data.LeAudioStateMachine


def parse_bluetooth_crash_info(log_content: str) -> Sequence[str]:
  """Parses the BT manager log to collect crash information.

  For this function to work, we expect below log snippet from given log content:

  ===
  Bluetooth crashed 2 times
  12-17 10:23:00
  12-17 11:29:13
  ===

  If there is no crash, log will look like:
  ===
  Bluetooth crashed 0 times
  ===

  Args:
    log_content: The dumped BT manager log.

  Returns:
    Sequence of crash time string in format '%m-%d %H:%M:%S'.

  Raises:
    errors.LogParseError:
      Fail to parse the log. It doesn't contain the key words.
  """
  lines = log_content.split('\n')
  for line_num, line in enumerate(lines):
    match_object = re.search(
      r'Bluetooth crashed (?P<crash_time>\d+) time', line)
    if match_object is None:
      continue

    crash_time = int(match_object.group('crash_time'))
    if crash_time > 0:
      begin_crash_time_num = line_num + 1
      return [
          line.strip()
          for line in lines[begin_crash_time_num:begin_crash_time_num +
                            crash_time]
      ]
    return []

  raise errors.LogParseError(log_content)


def parse_bonded_device_info(log_content: str) -> list[BondedDeviceInfo]:
  """Parses the BT manager log to collect bonded device information.

  For this function to work, we expect below log snippet from given log content:

  ===
  Bonded devices:
    28:6F:40:57:AC:44 [ DUAL ] JBL TOUR ONE M2
    CC:98:8B:C0:F2:B8 [ DUAL ] WH-1000XM3
  ===

  If there is no bonded device, log will look like:
  ===
  Bonded devices:

  ===

  Args:
    log_content: The dumped BT manager log.

  Returns:
    List[BondedDevice] : Dataclass of BondedDevice.
      Ex:
        [BondedDevice(mac_address='74:45:CE:F2:0F:EA',
                      device_name='WI-XB400',
                      device_type='DUAL')]
  Raises:
    errors.LogParseError:
      Fail to parse the log. It doesn't contain the key words.
  """
  if re.search(r'Bonded devices:\n', log_content) is not None:
    output = re.finditer(
      r'(?P<mac_address>\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})'
      r'\s\[\s+(?P<device_type>.*?)\s+\]\s(?P<device_name>.*?)\n',
      log_content,
    )
    bonded_devices = []
    for device in output:
      mac_address = device.group('mac_address')
      device_type = constants.BluetoothDeviceType.from_str(
          device.group('device_type'))
      device_name = device.group('device_name')
      bonded_devices.append(
        BondedDeviceInfo(
            mac_addr=mac_address,
            name=device_name,
            bt_type=device_type))

    return bonded_devices

  raise errors.LogParseError(log_content)


def get_ident_level(line: str) -> int:
  """Calculate the tab size of text.

  Args:
      line (str): Content per line

  Returns:
      int: size of the tab
  """
  return len(line) - len(line.lstrip())


def set_dataclass_attr(data_class_obj, k, v) -> None:
  """Set attribute for a dataclass"""
  field_names = [f.name for f in fields(data_class_obj)]
  if k in field_names:
    setattr(data_class_obj, k, v)
  else:
    data_class_obj.others[k] = v


def get_section_object(parent_section: object, sub_section_name: str,
                       key: str, value: str) -> object:
  """Adding subsection to parent section, and change the pointer to subsection.

  Args:
      parent_section (object): Dataclass of the parent section
      sub_section_name (str): Title of the subsection
      key (str): key of the data
      value (str): value of the data

  Returns:
      object: dataclass of subsection
  """
  match sub_section_name:
    case "ActiveGroupsinformation":
      new_section_obj = ActiveGroupInfo()
      parent_section.active_group_list.append(new_section_obj)
      return new_section_obj
    case "Group":
      new_section_obj = GroupInfo()
      set_dataclass_attr(new_section_obj, key, value)
      parent_section.group_list.append(new_section_obj)
      return new_section_obj
    case "mDevice":
      new_section_obj = DeviceInfo()
      set_dataclass_attr(new_section_obj, key, value)
      parent_section.device_list.append(new_section_obj)
      return new_section_obj
    case "StateMachineLog":
      new_section_obj = StateMachineLog()
      parent_section.state_machine_list.append(new_section_obj)
      return new_section_obj
    case "LeAudioStateMachine":
      new_section_obj = LeAudioStateMachine()
      parent_section.le_audio_state_machine_list.append(new_section_obj)
      return new_section_obj


def parse_le_audio_service_info(log_content: str) -> LeAudioServiceInfo:
  """Parses the BT manager log to collect LE audio service information.

  For this function to work, we expect below log snippet from given log content:

  ===
  Profile: LeAudioService
    isDualModeAudioEnabled: false
    Active Groups information:
      currentlyActiveGroupId: 1
      mActiveAudioOutDevice: XX:XX:XX:XX:38:31
  ===

  If there is no LE audio service, log will look like:
  ===
  Profile: LeAudioService
    isDualModeAudioEnabled: false
    Active Groups information:
      currentlyActiveGroupId: -1
      mActiveAudioOutDevice: null

  ===

  Args:
    log_content: The dumped BT manager log.

  Returns:
    LeAudioServiceInfo : Dataclass of LeAudioService.

  Raises:
    errors.LogParseError:
      Fail to parse the log. It doesn't contain the key words.
  """
  stack = []
  key = value = None
  current_ident_level = 2
  root_sect_obj = cur_sect_obj = LeAudioServiceInfo()
  previous_key = None
  if "Profile: LeAudioService" in log_content:
    for part_content in log_content.split("\n\n"):
      if "Profile: LeAudioService" not in part_content:
        continue
      for line in part_content.split("\n")[1:]:
        ident_level = get_ident_level(line)
        if ident_level == 2 and type(cur_sect_obj) not in [
            LeAudioServiceInfo, ActiveGroupInfo, GroupInfo, DeviceInfo, ]:
          cur_sect_obj, current_ident_level = stack.pop()
        line = re.sub(r'\s', '', line)

        if not line:
          continue

        if ident_level > current_ident_level:
          new_sect_obj = get_section_object(
            cur_sect_obj, previous_key, key, value)
          del cur_sect_obj.others[previous_key]
          stack.append((cur_sect_obj, current_ident_level))
          current_ident_level = ident_level
          cur_sect_obj = new_sect_obj

        elif current_ident_level > ident_level:
          cur_sect_obj, current_ident_level = stack.pop()

        first_mark = line.find("=") if line.find(":") < 0 else line.find(":")
        key = line[:first_mark]
        value = line[first_mark+1:]

        set_dataclass_attr(cur_sect_obj, key, value)
        previous_key = key

    return root_sect_obj

  raise errors.LogParseError(log_content)
