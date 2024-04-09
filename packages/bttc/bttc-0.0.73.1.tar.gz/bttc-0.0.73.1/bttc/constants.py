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

"""Module to hold constants used in BT operations."""
import enum
import re


ADB_SHELL_CMD_OUTPUT_ENCODING = 'utf-8'

# Logcat message timestamp format
LOGCAT_DATETIME_FMT = '%m-%d %H:%M:%S.%f'

LOGTCAT_MSG_PATTERN = re.compile(
    r'(?P<datetime>[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}.[\d]{3})(?P<message>.+$)')  # noqa: E501


class BluetoothAdapterState(enum.IntEnum):
  """Enum class for Bluetooth Adapter state."""
  STATE_UNKNOWN = -1
  STATE_OFF = 10
  STATE_TURNING_ON = 11
  STATE_ON = 12
  STATE_TURNING_OFF = 13
  STATE_BLE_TURNING_ON = 14
  STATE_BLE_ON = 15
  STATE_BLE_TURNING_OFF = 16

  @classmethod
  def from_int(cls, value: int) -> 'BluetoothAdapterState':
    for state in cls:
      if state.value == value:
        return state

    return cls.STATE_UNKNOWN


class BluetoothBondedState(enum.IntEnum):
  """Enum class for bluetooth bonded state.

  The enumeration here should sync up with go/bluetooth_bonded_state_enum
  """
  UNKNOWN = 0
  NONE = 10
  BONDING = 11
  BONDED = 12

  @classmethod
  def from_int(cls, state: int) -> 'BluetoothBondedState':
    for bonded_state in cls:
      if bonded_state == state:
        return bonded_state

    return cls.UNKNOWN

  @classmethod
  def from_str(cls, d_type: str) -> 'BluetoothBondedState':
    for device_type in cls:
      if device_type.name == d_type:
        return device_type

    return cls.UNKNOWN


class BluetoothDeviceType(enum.IntEnum):
  """Enum class for bluetooth device types.

  The enumeration here should sync up with go/bluetooth_device_type_enum
  """
  UNKNOWN = 0
  CLASSIC = 1  # BREDR
  LE = 2  # LE only
  DUAL = 3  # BREDR and LE

  @classmethod
  def from_int(cls, d_type: int) -> 'BluetoothDeviceType':
    for device_type in cls:
      if device_type == d_type:
        return device_type

    return cls.UNKNOWN

  @classmethod
  def from_str(cls, d_type: str) -> 'BluetoothDeviceType':
    for device_type in cls:
      if device_type.name == d_type:
        return device_type

    return cls.UNKNOWN


class BluetoothProfile(enum.IntEnum):
  """Enum class for bluetooth profile types.

  The enumeration here should sync up with go/public_api_of_bt_profiles
  """
  HEADSET = 1
  A2DP = 2
  HEALTH = 3
  HID_HOST = 4
  PAN = 5
  PBAP = 6
  GATT = 7
  GATT_SERVER = 8
  MAP = 9
  SAP = 10
  A2DP_SINK = 11
  AVRCP_CONTROLLER = 12
  AVRCP = 13
  HEADSET_CLIENT = 16
  PBAP_CLIENT = 17
  MAP_MCE = 18
  HID_DEVICE = 19
  OPP = 20
  HEARING_AID = 21
  UNKNOWN = 99


class BluetoothConnectionPolicy(enum.IntEnum):
  """Enum class for bluetooth connection policy.

  Bluetooth connection policy is defined in go/public_api_of_bt_profiles
  """
  CONNECTION_POLICY_UNKNOWN = -1
  CONNECTION_POLICY_FORBIDDEN = 0
  CONNECTION_POLICY_ALLOWED = 100


class MediaCommandEnum(enum.Enum):
  """Enum class for media passthrough commands."""

  def __new__(cls, *args, **kwds):
    value = len(cls.__members__) + 1
    obj = object.__new__(cls)
    obj._value_ = value
    return obj

  def __init__(self, command, event_name):
    self.command = command
    self.event_name = event_name

  PLAY = 'play', 'playReceived'
  PAUSE = 'pause', 'pauseReceived'
  NEXT = 'skipNext', 'skipNextReceived'
  PREVIOUS = 'skipPrev', 'skipPrevReceived'
