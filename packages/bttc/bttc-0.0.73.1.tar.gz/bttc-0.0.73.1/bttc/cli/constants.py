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

"""Keep constants used in Cli module."""


class Color:
  """Terminal Color information."""

  # Color
  PURPLE = '\033[95m'
  CYAN = '\033[96m'
  DARKCYAN = '\033[36m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  DARK_RED = '\033[31m'

  # Set
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'
  END = '\033[0m'
  BLINK_SLOW = '\033[5m'

  # Combination
  BLINK_BOLD_RED_SLOW = BOLD + RED + BLINK_SLOW


def warning(message: str):
  print(
      f'{Color.BOLD}{Color.YELLOW}[WARNING]{Color.END} '
      f'{Color.YELLOW}{message}{Color.END}')
