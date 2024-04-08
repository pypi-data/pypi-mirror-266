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

"""Dataclass and enum used in HFP testing."""

from __future__ import annotations

import enum

from bttc.profiles.hfp import errors


@enum.unique
class CallStateEnum(str, enum.Enum):
  """Enum of phone call state."""
  RINGING = "RINGING"
  IDLE = "IDLE"
  DIALING = "DIALING"
  ACTIVE = "ACTIVE"
  ON_HOLD = "ON_HOLD"
  CONNECTING = "CONNECTING"
  CONNECTED = "CONNECTED"
  DISCONNECTING = "DISCONNECTING"
  DISCONNECTED = "DISCONNECTED"
  ANSWERING = "ANSWERING"
  ANSWERED = "ANSWERED"

  @classmethod
  def from_str(cls, name: str) -> CallStateEnum:
    """Turns string into call state enum.

    Args:
      name: Name of call state enum in string.

    Returns:
      Corresponding call state enum.

    Raises:
      UnknownCallStateError: Given call state name is unknown.
    """
    for call_state_enum in cls:  # pytype: disable=missing-parameter
      if name == call_state_enum.value:
        return call_state_enum

    raise errors.UnknownCallStateError(f"Unknown call state name={name}")
