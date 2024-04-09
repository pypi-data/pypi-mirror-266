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

"""BT working strategy module."""

import abc

from bttc import constants


class UnsupportedProfileConnectionError(Exception):
  """Error casued by unsupported connection of profile."""

  def __init__(self, profile: constants.BluetoothProfile):
    super().__init__()
    self._profile = profile

  def __str__(self):
    return f'Connection with profile={self._profile.name} is not supported yet!'


class ConnectionStrategy(abc.ABC):
  """Bluetooth profile connection strategy."""

  @abc.abstractmethod
  def is_connected(self) -> bool:
    """Checks the connection of target profile.

    Returns:
      True iff and target profile is connected.
    """
    raise NotImplementedError

  @abc.abstractmethod
  def connect(self, timeout_sec: int = 30) -> bool:
    """Builds connection of target profile.

    Args:
      timeout_sec: Number of seconds to wait for connection.

    Returns:
      True iff the connection is carried out successfully.
    """
    raise NotImplementedError
