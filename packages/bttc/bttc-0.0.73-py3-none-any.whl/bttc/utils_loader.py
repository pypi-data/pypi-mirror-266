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

"""Utility to load functional modules of device."""
from bttc import core
from bttc import ble_utils        # noqa: F401
from bttc import general_utils    # noqa: F401
from bttc import bt_utils         # noqa: F401
from bttc import wifi_utils       # noqa: F401
import dataclasses
import deprecation
import importlib
import pkgutil
from typing import Any


@dataclasses.dataclass
class FuncModuleInfo:
  name: str
  module: Any
  auto_load: bool = False

  @classmethod
  def from_module(cls, module):
    func_modu_info = FuncModuleInfo(
        name=module.BINDING_KEYWORD,
        module=module)
    if hasattr(module, 'AUTO_LOAD') and module.AUTO_LOAD:
      func_modu_info.auto_load = True

    return func_modu_info


def get_util_modules() -> dict[str, FuncModuleInfo]:
  """Gets utility modules."""
  loaded_module_info_map: dict[str, FuncModuleInfo] = {}
  utilit_module_set = set()
  for util_clz in core.UtilBase.__subclasses__():
    if util_clz.__module__ not in utilit_module_set:
      utilit_module_set.add(util_clz.__module__)
      loaded_module = importlib.import_module(util_clz.__module__)
      module_info = FuncModuleInfo.from_module(loaded_module)
      loaded_module_info_map[loaded_module.BINDING_KEYWORD] = module_info

  return loaded_module_info_map


@deprecation.deprecated(
    deprecated_in='0.0.69.x',
    removed_in='0.0.70.x',
    details=(
        'This function is soon to be expired. '
        'Please use `get_util_modules` instead'))
def get_func_modules() -> dict[str, FuncModuleInfo]:
  loaded_module_info_map: dict[str, FuncModuleInfo] = {}
  candidate_module_names = (
      [name for _, name, _ in pkgutil.iter_modules(['bttc'])]
  )
  func_util_module_names = list(filter(
      lambda m: m.endswith('_utils'), candidate_module_names))

  if not func_util_module_names:
    for util_module in [general_utils, bt_utils]:
      module_info = FuncModuleInfo.from_module(util_module)
      loaded_module_info_map[util_module.BINDING_KEYWORD] = module_info
  else:
    for module_name in func_util_module_names:
      loaded_module = importlib.import_module(f'bttc.{module_name}')
      module_info = FuncModuleInfo.from_module(loaded_module)
      loaded_module_info_map[loaded_module.BINDING_KEYWORD] = module_info

  return loaded_module_info_map
