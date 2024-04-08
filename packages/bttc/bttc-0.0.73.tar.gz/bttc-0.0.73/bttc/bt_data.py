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

"""Module to hold dataclass or related data used in Bluetooth operations."""

import dataclasses
from bttc import constants
from typing import Any


@dataclasses.dataclass
class BondedDeviceInfo:
  """Information of a bonded device."""

  mac_addr: str
  bt_type: constants.BluetoothDeviceType
  name: str


@dataclasses.dataclass
class PairedDeviceInfo:
  """Information of a paired device."""

  mac_addr: str
  bt_type: constants.BluetoothDeviceType
  name: str
  uuids: list[str]
  bond_state: constants.BluetoothBondedState

  @classmethod
  def from_dict(
      cls, dict_data: dict[str, Any]) -> 'PairedDeviceInfo':
    name = dict_data['Name']

    # 'DEVICE_TYPE_DUAL' -> 'DUAL'
    bt_type = constants.BluetoothDeviceType.from_str(
        dict_data['DeviceType'].split('_')[-1])

    mac_addr = dict_data['Address']
    uuids = dict_data['UUIDs'] if 'UUIDs' in dict_data else []
    bond_state = constants.BluetoothBondedState.from_str(
        dict_data['BondState'].split('_')[-1])

    return PairedDeviceInfo(
        mac_addr=mac_addr,
        bt_type=bt_type,
        name=name,
        uuids=uuids,
        bond_state=bond_state)
