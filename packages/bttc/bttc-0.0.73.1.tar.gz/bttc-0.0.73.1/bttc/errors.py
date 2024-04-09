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

"""BTTC related errors."""


class Error(Exception):
  """A base class for errors related to BTTC."""


class AdbExecutionError(Error):
  """Failed in adb execution."""

  def __init__(
      self, return_code: int, error_msg: str, guiding_msg: str | None = None):
    guiding_msg = f'>>> {guiding_msg} <<<\n' if guiding_msg else ''
    message = f'''{guiding_msg}
    Failed in adb execution with return code={return_code}:
    {error_msg}'''
    super().__init__(message)


class AdbDeviceError(Error):
  """Failure related to device operation."""

  def __init__(self, output: str):
    super().__init__(
        f'Something wrong with device: {output}')


class AdbUnknownOutputError(Error):
  """Failed in searching/parsing adb output."""

  def __init__(self, output: str):
    super().__init__(
        f'Adb with unexpected output: {output}')


class MethodError(Error):
  """Failed in method call from modules."""

  def __init__(self, method_name: str, err_msg: str):
    super().__init__(f'{method_name} >>> {err_msg}')


class UnknownUtilityNameError(Error):
  """Unknown utility name error."""

  def __init__(self, unknown_utility_names: list[str]):
    super().__init__(
        f'Utility name(s)={unknown_utility_names} are not supported!')


class UnknownWiFiStatusError(Error):
  """Unknown WiFi status error."""

  def __init__(self, adb_output: str):
    super().__init__(
        f'Unknown WiFi status from adb output={adb_output}')


class LogParseError(Error):
  """Log Parser Error"""
  def __init__(self, log_content: str) -> None:
    super().__init__(f'Log Parser Error:\n Content:{log_content}')
