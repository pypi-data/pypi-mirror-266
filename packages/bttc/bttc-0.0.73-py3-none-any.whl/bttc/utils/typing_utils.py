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

"""Utility to deal with common typing."""

import logging
from typing import Any, Union, Optional, Protocol

from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb
from mobly.controllers.android_device_lib import service_manager
from mobly.controllers.android_device_lib import snippet_client_v2 as snippet_client  # noqa
from bttc.mobly_android_device_lib.services import sl4a_service


class LogProtocol(Protocol):
  """Protcol to facilitate typing hint for loggers in logging."""

  def info(self, msg: str, *args, **kwargs) -> None:
    ...

  def debug(self, msg: str, *args, **kwargs) -> None:
    ...

  def warning(self, msg: str, *args, **kwargs) -> None:
    ...

  def error(self, msg: str, *args, **kwargs) -> None:
    ...


class AdbDevice(Protocol):
  """Protocol to facilitate typing hint for device with adb property."""
  adb: adb.AdbProxy
  log: Union[logging.LoggerAdapter, logging.Logger]
  services: service_manager.ServiceManager

  def root_adb(self):
    ...


class AdbWithLogpathDevice(AdbDevice, Protocol):
  """AdbDevice + logpath attribute."""
  log_path: str


class AndroidLike(AdbDevice, Protocol):
  """Android like device."""
  model: str
  log_path: str
  build_info: dict[str, str]
  serial: str
  sl4a: Optional[sl4a_service.Sl4aService]
  ed: Any

  def reboot(self) -> None:
    ...

  def load_snippet(self, name: str, package: str):
    ...

  def wait_for_boot_completion(
      self,
      timeout: int = android_device.DEFAULT_TIMEOUT_BOOT_COMPLETION_SECOND):
    ...


class AndroidLikeWithMBS(AndroidLike, Protocol):
  """Android like device."""
  mbs: snippet_client.SnippetClientV2
