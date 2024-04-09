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

"""Porting version of module tl4a_snippet_client.py in G3"""

from bttc.utils import logcat
import dataclasses
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import snippet_client_v2
from mobly.snippet import errors
import threading
from typing import Any


_SNIPPETRUNNER_TAG_OF_LOGCAT = 'com.google.system.telephony.SnippetRunner'
_TL4A_MODULE_NAME = 'tl4a_api.py'
_SYSTEM_PACKAGE_NAME = 'com.google.system.telephony'
_TL4A_SNIPPET_NAME = 'tl4a'
_DEFAULT_CALL_FUNCTIONS_FOR_SKIP = (
    'send_rpc_request',
    '_update_tl4a_usage_record',
    '_rpc',
    'rpc_call',
    '_get_tl4a_callers',
)
_DEFAULT_CALL_SNIPPET_FOR_SKIP = 'setConfigurator'
_DEFAULT_CALL_FUNCTIONS_FOR_BREAKER = (
    'exec_one_test', '_initial_uidevice'
)
_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
_TL4A_USAGE_RECORDING_LOCK = threading.Lock()


@dataclasses.dataclass
class _Tl4aCaller:
  """TL4A caller information.

  Attributes:
    caller_name: The name of the caller.
    caller_module: The module of the caller.
  """
  caller_name: str
  caller_module: str


class Tl4aSnippetClient(snippet_client_v2.SnippetClientV2):
  """Client for interacting with TL4A snippet server on Android Device.

  Attributes:
    force_restart: Force restart TL4A server when there is no response.
  """
  def __init__(
      self,
      package: str,
      ad: android_device.AndroidDevice,
      config: Any | None = None,
      record_tl4a_usage: bool = True,
      force_restart: bool = True,
  ):
    super().__init__(package, ad)
    self.tl4a_snippet_usage = None
    self.force_restart = force_restart

  def send_rpc_request(self, request: str) -> str:
    """Sends an RPC request to the server and receives a response.

    Args:
      request: str, the request to send the server.

    Returns:
      The string of the RPC response.

    Raises:
      errors.Error: if failed to send the request or receive a response.
      errors.ProtocolError: if received an empty response from the server.
      UnicodeError: if failed to decode the received response.
    """
    try:
      response = super().send_rpc_request(request)
    except errors.ProtocolError as protocol_error:
      _tl4a_no_response_detect(ad=self._device)
      if self.force_restart:
        if self.host_port in _list_occupied_adb_ports(ad=self._device):
          self.close_connection()
        self.start_server()
        self.make_connection()
        response = super().send_rpc_request(request)
      else:
        raise protocol_error
    return response

  def stop(self):
    """Release all the resources and record the tl4a_snippet_usage proto."""
    super().stop()


def _tl4a_no_response_detect(ad: android_device.AndroidDevice) -> None:
  """Detects the potential cause of TL4A generic no response.

  Args:
    ad: Mobly's Android controller object.
  """
  log = _get_precise_snippet_start_information_from_logcat(ad=ad)
  if log is None:
    ad.log.error(
        'TL4A no Response detected: TL4A service start information is missing'
        ' from Logcat.'
    )
    return
  snippet_start_time = log.timestamp
  snippet_pid = log.pid
  if logcat.check_mobly_logcat_alive(ad=ad):
    error_message = (
        'TL4A no response detected: Logcat service also stopped. Please check'
        ' the following:\n1. Server (Host): Overload or insufficient system'
        ' memory.\n2. Device: Hardware connection or unstable device.\n3.'
        ' Special command: After executing commands like "pm kill" or "am'
        ' force-stop", "iptables"...etc., please wait until the service and'
        ' device stabilize before loading the TL4A snippet.'
    )
    ad.log.error(error_message)
    return
  logcat.check_jdwp_connetion(
      ad=ad,
      process_id=snippet_pid,
      begin_time=snippet_start_time,
      end_time=None,
  )
  if logcat.check_process_id_not_been_killed_within_duration(
      ad=ad,
      process_id=snippet_pid,
      begin_time=snippet_start_time,
      end_time=None,
  ):
    ad.log.error('TL4A no response detected: Process has been killed.')


def _get_precise_snippet_start_information_from_logcat(
    ad: android_device.AndroidDevice,
) -> logcat.LogCat | None:
  """Gets the last snippet start information from logcat.

  Args:
    ad: Mobly's Android controller object.

  Returns:
    The Logcats object wrapped around the last parsed snippet start
    information from logcat.
  """
  logs = logcat.search_logcat(
      ad=ad,
      text='Snippet server started',
      tag=_SNIPPETRUNNER_TAG_OF_LOGCAT,
      priority=logcat.Priority.info,
  )
  if logs:
    return logs[-1]
  ad.log.info('TL4A snippet start time not found.')


def _list_occupied_adb_ports(ad: android_device.AndroidDevice):
  """Returns a list of occupied host ports from ADB.

  Args:
    ad: Mobly's Android controller object.
  """
  out = ad.adb.forward('--list')
  clean_lines = str(out, 'utf-8').strip().split('\n')
  used_ports = []
  for line in clean_lines:
    tokens = line.split(' tcp:')
    if len(tokens) != 3:
      continue
    used_ports.append(int(tokens[1]))
  return used_ports


def load_system_snippet(ad: android_device.AndroidDevice):
  """Loads TL4A snippet."""
  name = _TL4A_SNIPPET_NAME
  snippet_client = ad.services.snippets.get_snippet_client(name)
  if snippet_client is not None:
    return

  client = Tl4aSnippetClient(
      package=_SYSTEM_PACKAGE_NAME,
      ad=ad)
  client.initialize()
  # pylint: disable=protected-access
  ad.services.snippets._snippet_clients[name] = client
