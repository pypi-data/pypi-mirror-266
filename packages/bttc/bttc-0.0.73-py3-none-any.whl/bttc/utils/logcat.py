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

"""Utils for logcat control."""

from collections.abc import Sequence
import dataclasses
import datetime
import enum
import re

from mobly.controllers import android_device

_FORMAT_TIMESTAMP = '%Y%m-%d %H:%M:%S.%f'
_FORMAT_DEVICE_TIMESTAMP = '%Y%m-%d %H:%M:%S'
_LOGCAT_PATTERN = (
    r'(?P<datetime>\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}.\d{1,3}) '
    r'+(?P<pid>\d+) +(?P<tid>\d+) +(?P<priority>[VDIWEFS]) +(?P<tag>[\w_.]+) '
    r'*:(?P<text>.+)')


class Priority(enum.Enum):
  """Defines Logcat priority (V: lowest priority > S: highest priority)."""
  verbose = 'V'
  debug = 'D'
  info = 'I'
  warning = 'W'
  error = 'E'
  fatal = 'F'
  silent = 'S'


@dataclasses.dataclass(frozen=True)
class LogCat:
  """Defines logcat message as Logcat object."""
  timestamp: datetime.datetime
  pid: str
  tid: str
  priority: Priority
  tag: str
  text: str


def search_logcat(
    ad: android_device.AndroidDevice,
    text: str | None = None,
    tag: str | None = None,
    priority: Priority | None = None,
    begin_time: datetime.datetime | None = None,
    end_time: datetime.datetime | None = None,
    logcat_path: str | None = None,
    time_zone_alignment: bool = True) -> Sequence[LogCat]:
  """Searches logcat with given match items.

  The structure of logcat.
  ----------------------------------------------------------------
  |Date  |Time         |PID  |TID  |Priority |Tag      | Text    |
  ----------------------------------------------------------------
  |12-28 |21:52:20.674 |2385 |2488 |I        |Watchcat |Started. |
  ----------------------------------------------------------------

  Args:
    ad: Mobly's Android controller object.
    text: Matching text to search.
    tag: Matching tag to search.
    priority: Matching Priority object to search.
    begin_time: Time stamps later than begin_time will be captured.
    end_time: Time stamps earlier than end_time will be captured.
    logcat_path: The path of a specific file in which the search should be
      performed. If None the path will be the default device log path.
    time_zone_alignment: Search logcat by the current time of the device.

  Returns:
    A List of LogCat object.
  """
  if logcat_path is None:
    logcat_path = ad.adb_logcat_file_path
  if time_zone_alignment:
    now = get_currect_device_time(ad)
  else:
    now = datetime.datetime.now()
  logs = []
  current_year = now.year
  with open(logcat_path, 'r', encoding='utf-8', errors='ignore') as logcat_file:
    lines = logcat_file.readlines()
  for line in lines:
    match = re.search(_LOGCAT_PATTERN, line)
    if match is None:
      continue

    timestamp = datetime.datetime.strptime(
        str(current_year) + match.group('datetime'), _FORMAT_TIMESTAMP)
    #  For year shift workaround.
    if (now - timestamp).days < -1:
      timestamp = timestamp - datetime.timedelta(days=365)
    if begin_time is not None and timestamp < begin_time:
      continue
    if end_time is not None and timestamp > end_time:
      continue

    log = LogCat(
        timestamp=timestamp,
        pid=match.group('pid'),
        tid=match.group('tid'),
        priority=Priority(match.group('priority')),
        tag=match.group('tag'),
        text=match.group('text'))
    if text is not None and text not in log.text:
      continue
    if tag is not None and tag not in log.tag:
      continue
    if priority is not None and priority != log.priority:
      continue
    logs.append(log)
  return logs


def get_currect_device_time(
    ad: android_device.AndroidDevice,
) -> datetime.datetime:
  """Returns the current device time.

  Args:
    ad: Mobly's Android controller object.
  """
  return datetime.datetime.strptime(
      ad.adb.shell(f'date +"{_FORMAT_DEVICE_TIMESTAMP}"')
      .decode('utf-8')
      .strip(),
      _FORMAT_DEVICE_TIMESTAMP,
  )


def check_mobly_logcat_alive(
    ad: android_device.AndroidDevice,
    tolerance_seconds: datetime.timedelta = datetime.timedelta(seconds=5)
) -> bool:
  """Returns True if Mobly logcat is alive.

  Check if the timestamp of the last logcat is within a 5-second difference
  from the current device time.

  Args:
    ad: Mobly's Android controller object.
    tolerance_seconds: If there are no updates from the logcat service beyond
      this  seconds, it is considered not alive.
  """
  current_timestamp = get_currect_device_time(ad)
  logs = search_logcat(ad=ad)
  if not logs:
    ad.log.error('Logcat not found.')
    return False
  elif logs[-1].timestamp + tolerance_seconds < current_timestamp:
    ad.log.error(
        'Logcat service has already stopped since'
        f' {logs[-1].timestamp} (current timestamp: {current_timestamp}).'
        ' Please consider that the device connection may have been lost or'
        ' become unstable for a while. '
    )
    return False
  return True


def check_jdwp_connetion(
    ad: android_device.AndroidDevice,
    process_id: str,
    begin_time: datetime.datetime | None,
    end_time: datetime.datetime | None,
) -> bool:
  """Returns True if there's an adb (jdwp) connection from the process ID.

  Parsing logcat and match Java Debug Wire Protocol (jdwp) connetion from given
  process ID within duration.

  Args:
    ad: Mobly's Android controller object.
    process_id: Android process ID for searching in logcat.
    begin_time: Time stamps later than begin_time will be checked.
    end_time: Time stamps earlier than end_time will be checked.
  """
  logs = search_logcat(
      ad=ad,
      text=f'jdwp connection from {process_id}',
      tag='adbd',
      priority=Priority.info,
      begin_time=begin_time,
      end_time=end_time,
  )
  if logs:
    ad.log.info(
        ' adb (jdwp) connection from the process ID when: '
        f'{logs[-1].timestamp.strftime(_FORMAT_TIMESTAMP)}')
    return True
  return False


def check_process_id_not_been_killed_within_duration(
    ad: android_device.AndroidDevice,
    process_id: str,
    begin_time: datetime.datetime | None,
    end_time: datetime.datetime | None,
) -> bool:
  """Returns True if the Process ID is not killed within duration.

  Args:
    ad: Mobly's Android controller object.
    process_id: Android process ID for searching in logcat.
    begin_time: Time stamps later than begin_time will be checked.
    end_time: Time stamps earlier than end_time will be checked.
  """
  logs = search_logcat(
      ad=ad,
      text=f'Killing {process_id}',
      tag='ActivityManager',
      begin_time=begin_time,
      end_time=end_time,
  )
  if logs:
    ad.log.error(
        f'Process ID: {process_id} has been killed when: '
        f'{logs[-1].timestamp.strftime(_FORMAT_TIMESTAMP)}'
    )
    return False
  return True
