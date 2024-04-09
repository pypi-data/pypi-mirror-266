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

"""Utility to produce desired device."""
import logging

from mobly.controllers import android_device
from bttc.mobly_android_device_lib import tl4a_snippet_client
from bttc.mobly_android_device_lib.services import sl4a_service

from snippet_uiautomator import uiautomator
from typing import TypeAlias, Union


GeneralDevice: TypeAlias = android_device.AndroidDevice


def load_sl4a(device: GeneralDevice):
  """Loads SL4A service in given device."""
  if device.services.has_service_by_name('sl4a'):
    logging.info('SL4A is already loaded in device=%s!', device)
    return

  logging.info('Registering service "sl4a" in device=%s...', device)
  device.services.register('sl4a', sl4a_service.Sl4aService)


def get(
    ad: Union[GeneralDevice, str],
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False) -> GeneralDevice:
  """Produces desired device.

  Args:
    init_mbs: True to register service `snippets` in provided device.
    init_sl4a: True to register service `sl4a` in provided device.
    init_snippet_uiautomator: True to register service `uiautomator` in provided
        device.
    init_tl4a: True to register service `tl4a` in provided device.

  Returns:
    The produced device object.
  """
  device: GeneralDevice | None = None
  if isinstance(ad, str):
    device = android_device.create([{'serial': ad}])[0]
  else:
    device = ad

  if all([
      (init_mbs or init_snippet_uiautomator),
      'snippets' not in device.services.list_live_services()]):
    logging.info('Register service "mbs" in device=%s...', device)
    device.load_snippet(
        'mbs',
        'com.google.android.mobly.snippet.bundled')

  if init_sl4a:
    load_sl4a(device)

  if init_tl4a:
    tl4a_snippet_client.load_system_snippet(device)

  if all([
      init_snippet_uiautomator,
      'uiautomator' not in device.services.list_live_services()]):
    if 'ui_dump' in device.services.list_live_services():
      device.log.info(
          '`ui_dump` is detected and it will conflict with snippet uiautomator!'
          ' Unloading it so to register snippet uiautomator next...')
      device.services.unregister('ui_dump')

    device.services.register(
        'uiautomator', uiautomator.UiAutomatorService)

  if all([
      init_snippet_uiautomator,
      'uiautomator' not in device.services.list_live_services()]):
    device.services.register(
        'uiautomator', uiautomator.UiAutomatorService)

  logging.info(
      '%s has registered service(s): %s',
      device, device.services.list_live_services())

  return device
