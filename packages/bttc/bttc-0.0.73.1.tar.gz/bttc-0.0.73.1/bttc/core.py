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

"""Module to put core class or settings."""
from functools import partial, update_wrapper
from mobly.controllers import android_device
from typing import Any, TypeAlias


ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


class UtilBase:
  """Utility base class."""

  NAME: str = 'Unknown'
  DESCRIPTION: str = '?'

  def __init__(self, ad: ANDROID_DEVICE):
    """Initializes the GModule utility class.

    Args:
        ad:  The Android device object to control.
    """
    self._ad: ANDROID_DEVICE = ad

  def _bind(self, target_func: Any, method_name: str | None = None):
    if not method_name:
      method_name = target_func.__name__

    setattr(self, method_name, partial(target_func, self._ad))
    update_wrapper(getattr(self, method_name), target_func)
