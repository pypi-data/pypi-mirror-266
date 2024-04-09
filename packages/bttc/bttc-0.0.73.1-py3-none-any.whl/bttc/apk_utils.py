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

"""Utility to support Apk related operations."""

import io
import logging
import os

from typing import Iterable, Sequence

from bttc import core
from bttc.utils import device_factory
from bttc.utils import typing_utils

from mobly import utils
from mobly.controllers.android_device import AndroidDevice
from mobly.controllers.android_device_lib import adb


AUTO_LOAD = True
AndroidLike = typing_utils.AndroidLike
BINDING_KEYWORD = 'apk'
DEFAULT_TIMEOUT_INSTALL_APK_SEC = 300
MBS_PACKAGE_NAME = 'com.google.android.mobly.snippet.bundled'
SL4A_PACKAGE_NAME = 'com.googlecode.android_scripting'
UIAUTOMATOR_PACKAGE_NAME = 'com.google.android.mobly.snippet.uiautomator'


class ApkModule(core.UtilBase):
  """Apk module to hold apk related functions."""

  NAME = BINDING_KEYWORD
  DESCRIPTION = 'Utility to support Apk related operations.'

  def __init__(self, ad: AndroidLike):
    super().__init__(ad)
    self._bind(install)
    self._bind(install_mbs)
    self._bind(install_sl4a)
    self._bind(is_package_installed)
    self._bind(is_mbs_installed)
    self._bind(is_sl4a_installed)
    self._bind(is_uiautomator_installed)
    self._bind(list_packages)


def bind(
    ad: AndroidLike | str,
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False,) -> AndroidLike:
  """Binds the input device with functions defined in current module.

  Sample Usage:
  ```python
  >>> from bttc import apk_utils
  >>> ad = apk_utils.bind('07311JECB08252', init_mbs=True, init_sl4a=True)
  >>> ad.apk.is_sl4a_installed()
  True
  ```

  Args:
    ad: Android like device object or str of device's serial.
    init_mbs: True to initialize device with service MBS.
    init_sl4a: True to initialize device with service SL4A.
    init_snippet_uiautomator: True to initialize device with service
        uiautomator.
    init_tl4a: If True, initializes TL4A.

  Returns:
    Device binded with BLE module.
  """
  device = device_factory.get(
      ad, init_mbs=init_mbs, init_sl4a=init_sl4a,
      init_snippet_uiautomator=init_snippet_uiautomator,
      init_tl4a=init_tl4a)
  device.load_config({BINDING_KEYWORD: ApkModule(device)})

  return device


def _execute_adb_install(device: AndroidDevice,
                         install_args: Sequence[str],
                         timeout: int) -> None:
  """Executes the adb install command.

  Args:
    device: AndroidDevice, Mobly's Android controller object.
    install_args: list of strings, the args to be added to `adb install` cmd.
    timeout: int, the number of seconds to wait before timing out.

  Raises:
    AdbError: Installation failed.
  """
  # Execute the install cmd.
  stderr_buffer = io.BytesIO()
  stdout = device.adb.install(
      install_args, stderr=stderr_buffer, timeout=timeout)
  stderr = stderr_buffer.getvalue().decode('utf-8').strip()
  if not _is_apk_install_success(stdout, stderr):
    # Poll the popup handling result only if the installation failed.
    adb_cmd = 'adb -s %s install %s' % (device.serial, ' '.join(install_args))
    raise adb.AdbError(cmd=adb_cmd, stdout=stdout, stderr=stderr, ret_code=0)


def _is_apk_install_success(stdout: bytes, stderr: str) -> bool:
  """Determines if an APK installation via 'adb install' was successful.

  Args:
    stdout: The standard output of the 'adb install' command.
    stderr: The standard error output of the 'adb install' command.

  Returns:
    True iff the installation succeeded.
  """
  if utils.grep('Failure', stdout):
    return False

  return any([not stderr, stderr == 'Success', 'waiting for device' in stderr])


def _is_min_sdk_int(device, min_sdk):
  """Checks if a device's SDK version is at least a certain number.

  Args:
    device: AndroidDevice object initialized for curator test.
    min_sdk: int, the minimum SDK version required.

  Returns:
    True if the device's SDK is not smaller than the min_sdk.
  """
  # Add one to api level for pre-release builds
  api_level = int(device.build_info['build_version_sdk'])
  if device.build_info['build_version_codename'] != 'REL':
    api_level += 1

  return api_level >= min_sdk


def is_mbs_installed(ad: AndroidLike):
  """Checks if MBS (a.k.a mobly bundled snippets) is installed or not.

  Args:
    ad: Android like device.

  Returns:
    True iff MBS is installed.
  """
  return is_package_installed(ad, MBS_PACKAGE_NAME)


def install(
    ad: AndroidDevice,
    apk_path: str,
    replace_exist_app: bool = True,
    allow_test_packages: bool = False,
    timeout: int = DEFAULT_TIMEOUT_INSTALL_APK_SEC,
    user_id: int | None = None,
    params: Iterable[str] | None = None,
) -> set[str]:
  """Install an apk on an Android device.

  Args:
    ad: AndroidDevice, Mobly's Android controller object.
    apk_path: string, file path of an apk file.
    replace_exist_app: True to replace existing application.
    timeout: int, the number of seconds to wait before timing out.
    user_id: int, the ID of the user to install the apk for. For SDK>=24,
        install for the current user by default. Android's multi-user support
        did not realistically work until SDK 24.
    params: string list, additional parameters included in the adb install cmd.

  Raises:
    AdbError: Installation failed.
    ValueError: Attempts to set user_id on SDK<24.

  Returns:
    Installed package set.
  """
  orig_package_set = ad.apk.list_packages()
  apk_path = os.path.expanduser(apk_path)
  android_api_version = int(ad.build_info['build_version_sdk'])
  if user_id is not None and android_api_version < 24:
    raise ValueError('Cannot specify `user_id` for device below SDK 24.')

  args = []
  if replace_exist_app:
    args.append('-r')

  if allow_test_packages:
    args.append('-t')

  if android_api_version >= 24:
    if user_id is None:
      user_id = ad.adb.current_user_id
    args = ['--user', str(user_id)] + args
  if android_api_version >= 23:
    args.append('-g')
  if android_api_version >= 17:
    args.append('-d')
  if _is_min_sdk_int(ad, 34):
    args.append('--bypass-low-target-sdk-block')

  args += params or []
  args.append(apk_path)
  _execute_adb_install(ad, args, timeout)
  current_package_set = ad.apk.list_packages()
  return current_package_set - orig_package_set


def install_mbs(
    ad: AndroidDevice,
    apk_path: str,
    replace_exist_app: bool = True,
    timeout: int = DEFAULT_TIMEOUT_INSTALL_APK_SEC,
) -> set[str]:
  """Installs MBS by given apk path.

  Args:
    ad: AndroidDevice, Mobly's Android controller object.
    apk_path: string, file path of an apk file.
    replace_exist_app: True to replace existing application.
    timeout: int, the number of seconds to wait before timing out.

  Returns:
    Installed package set.
  """
  if not replace_exist_app and is_sl4a_installed(ad):
    logging.info('MBS is already installed in %s!', ad)
    return {}

  return install(
      ad=ad,
      apk_path=apk_path,
      replace_exist_app=replace_exist_app,
      params=['-g'])


def install_sl4a(
    ad: AndroidDevice,
    apk_path: str,
    replace_exist_app: bool = True,
    timeout: int = DEFAULT_TIMEOUT_INSTALL_APK_SEC,
) -> set[str]:
  """Installs SL4A by given apk path.

  Args:
    ad: AndroidDevice, Mobly's Android controller object.
    apk_path: string, file path of an apk file.
    replace_exist_app: True to replace existing application.
    timeout: int, the number of seconds to wait before timing out.

  Returns:
    Installed package set.
  """
  if not replace_exist_app and is_sl4a_installed(ad):
    logging.info('SL4A is already installed in %s!', ad)
    return {}

  return install(
      ad=ad,
      apk_path=apk_path,
      replace_exist_app=replace_exist_app,
      params=['-t'])


def is_package_installed(
    ad: AndroidLike, package_name: str) -> bool:
  """Checks if the given package name is installed or not.

  Args:
    ad: Android like device.
    package_name: Apk package name.

  Returns:
    True iff the given package name is installed.
  """
  shell_cmd = (
      f'pm list packages | grep -i "^package:{package_name}$"'
      ' | wc -l')
  result = int(ad.adb.shell(shell_cmd).decode().strip())
  return bool(result)


def is_sl4a_installed(ad: AndroidLike):
  """Checks if SL4A package is installed or not.

  Args:
    ad: Android like device.

  Returns:
    True iff SL4A is installed.
  """
  return is_package_installed(ad, SL4A_PACKAGE_NAME)


def is_uiautomator_installed(ad: AndroidLike):
  """Checks if uiautomator package is installed or not.

  Args:
    ad: Android like device.

  Returns:
    True iff uiautomator is installed.
  """
  return is_package_installed(ad, UIAUTOMATOR_PACKAGE_NAME)


def list_packages(ad: AndroidLike) -> set[str]:
  """List installed packages."""
  installed_package_set = set()
  for installed_pkg in ad.adb.shell(
      'pm list packages').decode().strip().split('\n'):
    if installed_pkg.startswith('package:'):
      installed_package_set.add(installed_pkg[8:])

  return installed_package_set
