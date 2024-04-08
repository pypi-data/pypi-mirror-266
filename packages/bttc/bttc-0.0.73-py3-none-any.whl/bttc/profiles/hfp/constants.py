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

"""Constants used in HFP profile."""
import enum


@enum.unique
class AudioRoute(enum.Enum):
  """Enumeration of Audio source.

  The settings here have to sync up with "Constant for Audio Route" defined in
  go/audio_route_constant
  """
  EARPIECE = 'EARPIECE'
  BLUETOOTH = 'BLUETOOTH'
  SPEAKER = 'SPEAKER'
  WIRED_HEADSET = 'WIRED_HEADSET'
  WIRED_OR_EARPIECE = 'WIRED_OR_EARPIECE'
