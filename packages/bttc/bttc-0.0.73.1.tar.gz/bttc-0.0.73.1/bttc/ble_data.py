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

"""Module to hold dataclass or related data used in Bluetooth BLE."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActiveGroupInfo:
  currentlyActiveGroupId: int | None = None
  mActiveAudioOutDevice: str | None = None
  mActiveAudioInDevice: str | None = None
  mUnicastGroupIdDeactivatedForBroadcastTransition: int | None = None
  mExposedActiveDevice: str | None = None
  mHfpHandoverDevice: Any | None = None
  mLeAudioIsInbandRingtoneSupported: str | None = None
  others: dict[str, str] = field(default_factory=dict)


@dataclass
class GroupInfo:
  Group: str | None = None
  isActive: str | None = None
  isConnected: str | None = None
  mDirection: int | None = None
  grouplead: str | None = None
  others: dict[str, str] = field(default_factory=dict)


@dataclass
class LeAudioStateMachine:
  totalrecords: int | None = None
  others: dict[str, str] = field(default_factory=dict)


@dataclass
class StateMachineLog:
  le_audio_state_machine_list: list[LeAudioStateMachine] = field(
    default_factory=list)
  curState: str | None = None
  mDevInbandRingtoneEnabled: bool | None = None
  mSinkAudioLocation: int | None = None
  mDirection: int | None = None
  others: dict[str, str] = field(default_factory=dict)


@dataclass
class DeviceInfo:
  mDevice: str | None = None
  StateMachine: str | None = None
  state_machine_list: list[StateMachineLog] = field(default_factory=list)
  others: dict[str, str] = field(default_factory=dict)


@dataclass
class LeAudioService:
  isDualModeAudioEnabled: str | None = None
  active_group_list: list[ActiveGroupInfo] = field(default_factory=list)
  group_list: list[GroupInfo] = field(default_factory=list)
  device_list: list[DeviceInfo] = field(default_factory=list)
  others: dict[str, str] = field(default_factory=dict)
