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

"""Entry point of BTTC Cli prompt."""

import cmd2
import copy
import contextlib
import datetime
import functools
import importlib.util
import inspect
import logging
import mobly
import os
import pathlib
from ppadb import client
from pprint import pprint
import re
import sys

import bttc
from bttc import constants as bttc_constants
from bttc.cli import constants
from bttc.utils import device_factory


Color = constants.Color
EXIST_MSG = 'Welcome to use BTTC Cli and see you next time!'
MAIN_COMMANDS = "Main Commands"

select_parser = cmd2.Cmd2ArgumentParser()
select_parser.add_argument(
    '-s', '--serial', type=str, default=None, help='DUT serial')

logcat_filter_parser = cmd2.Cmd2ArgumentParser()
logcat_filter_parser.add_argument(
    '--logcat_wait_sec', type=int, default=10,
    help='Time in sec to follow logcat.')
logcat_filter_parser.add_argument(
    '--logcat_only_match', type=bool, default=False,
    help='Setup to show only matched line')

load_cmd2_commandset_parser = cmd2.Cmd2ArgumentParser()
load_cmd2_commandset_parser.add_argument(
    '-p', '--cmd2_module_path', type=str, default=None,
    help='Cmd2 module path where holds command set class.')


def dec_require_dut(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    self = args[0]
    is_dut_ready = False
    if isinstance(self, BttcCmdApp) and self._dut:
      is_dut_ready = True
    elif hasattr(self, '_app') and self._app._dut:
      is_dut_ready = True

    if not is_dut_ready:
      logging.warning('Please select your DUT first!')
      return

    return func(*args, **kwargs)

  return wrapper


def dec_require_sl4a(func):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    self = args[0]
    is_sl4a_ready = False
    if isinstance(self, BttcCmdApp) and self._dut:
      is_sl4a_ready = 'sl4a' in self._dut.services.list_live_services()
    elif hasattr(self, '_app') and self._app._dut:
      is_sl4a_ready = 'sl4a' in self._app._dut.services.list_live_services()

    if not is_sl4a_ready:
      logging.warning('Please load SL4A in DUT first!')
      return

    return func(*args, **kwargs)

  return wrapper


@cmd2.with_default_category('john_manual')
class TestCommandSet(cmd2.CommandSet):
  def __init__(self, app: 'BttcCmdApp'):
    super().__init__()
    self._app = app
    self.namespace_history = []

  def do_john_work(self, args):
    print("!!! Do john's Customized command test works !!!")


@cmd2.with_default_category('device_config')
class DeviceConfigCommandSet(cmd2.CommandSet):
  def __init__(self, app: 'BttcCmdApp'):
    super().__init__()
    self._app = app
    self.namespace_history = []

  def _get_namespace_obj(self, namespace: str):
    namespaces = self._app._dut.gm.device_config.namespaces()
    if namespace not in namespaces:
      logging.warning('namespace="%s" does not exist!', namespace)
      return None

    return getattr(self._app._dut.gm.device_config, namespace)

  @dec_require_dut
  def do_device_config_get(self, args):
    """Gets device config setting.

    Input could be one of below case:
    1. <namespace> <setting_name>: e.g. "bluetooth INIT_default_log_level_str"
    2. <setting_name>: e.g. "INIT_default_log_level_str"

    For second case, the namespace will be 'bluetooth'.
    """
    input_info = args.split(' ')
    namespace = ''
    setting_name = ''
    if len(input_info) == 2:
      namespace, setting_name = input_info
    elif len(input_info) == 1:
      namespace = 'bluetooth'
      setting_name = input_info[0]
    else:
      logging.warning('Unknown input="%s"', args)
      return

    namespace_obj = self._get_namespace_obj(namespace)
    print(f'{namespace_obj[setting_name]}\n')

  @dec_require_dut
  def do_device_config_put(self, args):
    """Put device config setting.

    Usage:
      1. device_config_put <namespace> <setting_name> <setting_value>
      2. device_config_put <setting_name> <setting_value>

    For second case, default namespace will be "bluetooth"

    Example:
    ```python
    bttc/...> device_config_put le_audio_enabled_by_default true
    bttc/...> device_config_put bluetooth le_audio_enabled_by_default true
    ```
    """
    input_info = args.split(' ')
    namespace = ''
    setting_name = ''
    setting_value = ''
    if len(input_info) == 3:
      namespace, setting_name, setting_value = input_info
    elif len(input_info) == 2:
      setting_name, setting_value = input_info
      namespace = 'bluetooth'
    else:
      logging.warning('Unknown input="%s"', args)
      return

    namespace_obj = self._get_namespace_obj(namespace)
    namespace_obj[setting_name] = setting_value
    print(
        'Successful in putting device_config '
        f'{namespace}["{setting_name}"]={setting_value}\n')

  @dec_require_dut
  def do_list_namespace(self, args):
    namespace = str(args)
    namespace_obj = self._get_namespace_obj(namespace)
    if namespace_obj:
      settings = list(namespace_obj)
      if not settings:
        logging.warning(
            'No setting exist under namespace="%s"', namespace)
        return
      self._app.poutput(
          f'===== Settings under namespace="{args}" '
          f'({len(settings):,d}): =====')
      for setting in settings:
        if setting.err:
          logging.warning(setting)
        else:
          print(f'{setting.name}={setting.value}')

      print('')


@cmd2.with_default_category('Properties')
class PropsCommandSet(cmd2.CommandSet):
  def __init__(self, app: 'BttcCmdApp'):
    super().__init__()
    self._app = app
    self.property_key_history = []

  @dec_require_dut
  def do_airplane_mode_state(self, args):
    """Gets DUT's airplane mode state."""
    self._app.poutput(
        f'Airplane state: {self._app._dut.gm.airplane_mode_state}\n')

  @dec_require_dut
  def do_device_info(self, args):
    """Shows DUT device information."""
    device_info = copy.copy(self._app._dut.device_info)
    device_info['init_sl4a'] = self._app.dut_init_sl4a
    device_info['init_snippet_uiautomator'] = (
        self._app.dut_init_snippet_uiautomator)
    pprint(device_info)
    print('')

  @dec_require_dut
  def do_build_id(self, args):
    self._app.poutput(f'Model: {self._app._dut.build_id}\n')

  @dec_require_dut
  def do_getprop(self, property_key):
    """Gets system property of DUT.

    Usage: getprop <system_property_key>

    If <system_property_key> is not given, interactive prompt will be shown up
    to ask for the system property key to query.
    """
    property_key = property_key.strip()
    try:
      property_key = property_key or self._app.read_input(
          r"Property key (Empty to search all or add prefix"
          r" `re:` to make it RE)? ",
          history=self.property_key_history,
          completion_mode=cmd2.CompletionMode.CUSTOM).strip()
      property_key = property_key.strip()
      if property_key.startswith('"') and property_key.endswith('"'):
        property_key = property_key[1:-1]
      if property_key.startswith("'") and property_key.endswith("'"):
        property_key = property_key[1:-1]
      if property_key:
        self.property_key_history.append(property_key)
    except EOFError:
      pass

    properties = []
    if not property_key:
      properties = list(self._app._dut.gm.props)
    elif property_key.startswith('re:'):
      re_property_key = property_key[3:]
      properties = [
          p for p in list(self._app._dut.gm.props)
          if re.search(re_property_key, str(p.key))]
    else:
      property_val = self._app._dut.gm.props[property_key]
      property_str = f'[{property_key}]: [{property_val}]'
      print(f'{property_str}\n')
      return

    for p in properties:
      print(p)

    print(f'===== Total {len(properties):,d} property found =====\n')

  @dec_require_dut
  def do_model(self, args):
    self._app.poutput(f'Model: {self._app._dut.model}\n')

  @dec_require_dut
  def do_sdk(self, args):
    self._app.poutput(f'SDK: {self._app._dut.gm.sdk}\n')

  @dec_require_dut
  def do_setprop(self, input_str):
    """Sets system property of DUT.

    Usage: setprop <system_property_key> <system_property_val>

    If not enough arguments are given, an interactive prompt will show up to ask
    for the required information.
    """
    args = input_str.split(' ')
    if len(args) >= 1:
      property_key = args[0]
      property_val = ''.join(args[1:])

    try:
      property_key = property_key or self._app.read_input(
          "Property key? ",
          history=self.property_key_history,
          completion_mode=cmd2.CompletionMode.CUSTOM).strip()
      property_key = property_key.strip()
      if not property_key:
        logging.warning('Property key is not give!')
        return

      property_val = property_val or self._app.read_input("Property value? ")
      if not property_val:
        logging.warning('Property value is not give!')
        return

      self._app._dut.gm.props[property_key] = property_val
      self._app.poutput(f'Set {property_key}={property_val} done!\n')
    except EOFError:
      pass


@cmd2.with_default_category('BT')
class BTCommandSet(cmd2.CommandSet):
  def __init__(self, app: 'BttcCmdApp'):
    super().__init__()
    self._app = app

  @dec_require_dut
  def do_bonded_devices(self, args):
    """Gets DUT's bonded device information."""
    bonded_devices = self._app._dut.bt.bonded_devices
    self._app.poutput(f'Total {len(bonded_devices)} bonded devices:')
    for bonded_device in bonded_devices:
      print(f'\t{bonded_device}')

    print('')

  @dec_require_sl4a
  def do_sl4a_bonded_devices(self, args):
    """Shows bonded device(s)."""
    bonded_devices = self._app._dut.sl4a.bluetoothGetBondedDevices()
    if not bonded_devices:
      self._app.poutput('No bonded device!\n')
      return

    self._app.poutput(f'Total {len(bonded_devices)} bonded devices:')
    for d in bonded_devices:
      d['state'] = bttc_constants.BluetoothBondedState.from_int(d['state'])
      d['type'] = bttc_constants.BluetoothDeviceType.from_int(d['type'])
      print(f'\t- {d}')

    print('')

  crash_since_parser = cmd2.Cmd2ArgumentParser()
  crash_since_parser.add_argument(
      '--hour', type=int, default=-1,
      help='Look back for # hour(s).')
  crash_since_parser.add_argument(
      '-m', '--minute', type=int, default=-1,
      help='Look back for # minute(s).')

  @dec_require_dut
  @cmd2.with_argparser(crash_since_parser)
  def do_crash_since(self, args):
    """Collects crash information within certain time in the past."""
    search_datetime = self._app._dut.gm.device_datetime
    if args.hour > 0:
      search_datetime = (
          search_datetime - datetime.timedelta(hours=args.hour))

    if args.minute > 0:
      search_datetime = (
          search_datetime - datetime.timedelta(minutes=args.minute))

    if args.hour < 0 and args.minute < 0:
      self._app.poutput('Collects all crash...')
      search_datetime = None
    else:
      self._app.poutput(f'Collects crash after {search_datetime}...')

    crash_since_datetime_str = (
        datetime.datetime.strftime(
            search_datetime, bttc_constants.LOGCAT_DATETIME_FMT)
        if search_datetime else None)

    crash_info = self._app._dut.bt.crash_since(crash_since_datetime_str)
    self._app.poutput(f'{crash_info}\n')

  @dec_require_dut
  def do_enable_snoop_log(self, args):
    """Enables snoop log."""
    if self._app._dut.bt.enable_snoop_log():
      self._app.poutput('Snoop log is enabled!\n')
    else:
      self._app.poutput('Failed to set snoop log!\n')

  @dec_require_sl4a
  def do_sl4a_local_name(self, args):
    """Gets device's local name by SL4A."""
    device_name = self._app._dut.sl4a.bluetoothGetLocalName()
    self._app.poutput(f'Local name: {device_name}\n')

  @dec_require_sl4a
  def do_sl4a_mac_address(self, args):
    """Gets device's MAC address by SL4A."""
    mac_addr = self._app._dut.sl4a.bluetoothGetLocalAddress()
    self._app.poutput(f'MAC address: {mac_addr}\n')


@cmd2.with_default_category('UI')
class UICommandSet(cmd2.CommandSet):
  def __init__(self, app: 'BttcCmdApp'):
    super().__init__()
    self._app = app

  ui_dump_parser = cmd2.Cmd2ArgumentParser()
  ui_dump_parser.add_argument(
      'path', nargs='*',
      help='File path to dump the current UI page.')

  @dec_require_dut
  @cmd2.with_argparser(ui_dump_parser)
  def do_take_screenshot(self, args):
    """Takes screenshot of UI page and save it to host."""
    dump_path_list = args.path or ['/tmp/']
    for path in dump_path_list:
      with contextlib.suppress(FileNotFoundError):
        os.remove(path)
      self._app.poutput(f'Save UI screenshot to {path}...\n')
      self._app._dut.gm.take_screenshot(path)

    print('')

  @dec_require_dut
  @cmd2.with_argparser(ui_dump_parser)
  def do_ui_dump_to(self, args):
    """Dumps current UI page to host."""
    dump_path_list = args.path or ['/tmp/test.xml']
    for path in dump_path_list:
      self._app.poutput(f'Dump UI page to {path}...\n')
      self._app._dut.gm.get_ui_xml(path)

    print('')


class BttcCmdApp(cmd2.Cmd):
  """BTTC  cmd2 application."""
  MAIN_PROMPT = f'{Color.BOLD}{Color.BLUE}bttc>{Color.END} '
  DEVICE_PROMPT_PROMPT = (
      f'{Color.BOLD}{Color.BLUE}bttc/{Color.YELLOW}' + r'{serial}' +
      Color.BLINK_SLOW + '> ' + Color.END)

  def __init__(self, serial: str | None = None):
    super().__init__(
        shortcuts=cmd2.DEFAULT_SHORTCUTS,
        command_sets=[
            UICommandSet(self), PropsCommandSet(self), BTCommandSet(self),
            DeviceConfigCommandSet(self)])

    self.prompt = BttcCmdApp.MAIN_PROMPT
    self.adb = client.Client(host='localhost', port=5037)
    self.dut_init_snippet_uiautomator = True
    self.dut_init_sl4a = False
    self.add_settable(
        cmd2.Settable(
            'dut_init_snippet_uiautomator', bool,
            'Initialize snippet_uiautomator in DUT during selection.', self))
    self.add_settable(
        cmd2.Settable(
            'dut_init_sl4a', bool,
            'Initialize SL4A in DUT during selection.', self))

    self._dut = None
    if serial:
      self._init_dut(serial)

    self.logcat_pattern_history = []
    self.selected_device_history = [
        device.serial for device in self.adb.devices()]

  def _init_dut(self, serial: str):
    self._dut = bttc.get(
        serial,
        init_snippet_uiautomator=self.dut_init_snippet_uiautomator,
        init_sl4a=self.dut_init_sl4a)
    self.prompt = BttcCmdApp.DEVICE_PROMPT_PROMPT.format(serial=serial)

  def do_load_test_cmd2(self, args):
    self.register_command_set(TestCommandSet(self))

  @dec_require_dut
  def do_device_time(self, args):
    self.poutput(f'{self._dut.gm.device_datetime}\n')

  @cmd2.with_argparser(load_cmd2_commandset_parser)
  def do_load_cmd2_command_set(self, args):
    """Loads cmd2 command set from given module path."""
    target_cmd2_module_path = os.path.expanduser(args.cmd2_module_path)
    if not os.path.isfile(target_cmd2_module_path):
      logging.warning(
          'The given cmd2 module path "%s" does not exist!',
          target_cmd2_module_path)
      return

    self.poutput(
        f'Loading cmd command set from {target_cmd2_module_path}...')
    load_cmd2_module(self, target_cmd2_module_path)

  @dec_require_dut
  def do_load_sl4a(self, args):
    """Loads SL4A service in DUT."""
    device_factory.load_sl4a(self._dut)
    self.dut_init_sl4a = True

  @dec_require_dut
  @cmd2.with_argparser(logcat_filter_parser)
  def do_logcat_filter(self, args):
    pattern_list = []
    while True:
      try:
        pattern_str = self.read_input(
            "Pattern (enter nothing to stop)? ",
            history=self.logcat_pattern_history,
            completion_mode=cmd2.CompletionMode.CUSTOM).strip()
        pattern_str = pattern_str.strip()
        if not pattern_str:
          break

        if pattern_str.startswith('file:'):
          pattern_file_path = pattern_str.split(':')[1]
          if not os.path.isfile(pattern_file_path):
            logging.warning(
                'Pattern file=%s does not exist!', pattern_file_path)
            continue

          load_pattern_count = 0
          with open(pattern_file_path, 'r') as fo:
            for line in fo:
              pattern_str = line.strip()
              if pattern_str:
                pattern_list.append(pattern_str)
                load_pattern_count += 1

          self.poutput(
              f'Total {load_pattern_count} patterns loaded from '
              f'{pattern_file_path}\n')
        else:
          pattern_list.append(pattern_str)

      except EOFError:
        pass

    def hit_pattern(line):
      for pattern in pattern_list:
        if re.search(pattern, line):
          return True

      return False

    for line in self._dut.gm.follow_logcat_within(
        time_sec=args.logcat_wait_sec):
      if hit_pattern(line):
        print(f'{Color.BOLD}{Color.YELLOW}{line}{Color.END}')
      elif not args.logcat_only_match:
        print(f'{Color.GREEN}{line}{Color.END}')

    print('\n\n')

  @cmd2.with_category(MAIN_COMMANDS)
  @cmd2.with_argparser(select_parser)
  def do_select(self, args):
    """Selects DUT."""
    selected_serial = args.serial
    connected_device_serials = {
        device.serial: device for device in self.adb.devices()}
    if not args.serial or args.serial not in connected_device_serials.keys():
      for _ in range(5):
        if len(connected_device_serials) == 0:
          logging.warning('No device connected!')
          return
        elif len(connected_device_serials) == 1:
          selected_serial = list(connected_device_serials.items())[0][0]
          self.poutput('Only one deviect connected!')
          break
        self.poutput('Connected device(s): ')
        for pair in connected_device_serials.items():
          print(f'\t- {pair[0]}')

        print('')
        try:
          selected_serial = self.read_input(
              "Select? ",
              history=self.selected_device_history,
              completion_mode=cmd2.CompletionMode.CUSTOM,
              choices=list(connected_device_serials.keys()))
        except EOFError:
          pass
        else:
          if selected_serial in connected_device_serials.keys():
            self.selected_device_history.append(selected_serial)
            break
      else:
        self.poutput('Failed to select eligible device!')

    self.poutput(f'You select DUT with serial={selected_serial}\n')
    self._init_dut(selected_serial)

  @cmd2.with_category(MAIN_COMMANDS)
  def do_devices(self, _):
    """Self test command by list connected device(s)."""
    connected_devices = self.adb.devices()
    if not connected_devices:
      self.poutput("No device connected from host!")
      return

    self.poutput("Connected devices from host:")
    for device in connected_devices:
      print(f'\t- {device.serial}')

    print('')

  def free_dut(self):
    print('Releasing DUT resource...')
    if self._dut:
      stopped_services = []
      with contextlib.suppress(mobly.snippet.errors.ProtocolError):
        try:
          for service_name in self._dut.services._service_objects.keys():
            service = self._dut.services._service_objects[service_name]
            if service_name == 'sl4a':
              self.poutput('Stopping SL4A...')
              service._sl4a_client.host_port = None
              service._sl4a_client._client.close()
              service._sl4a_client.close_socket_connection()
              service.stop()
              continue

            self.poutput(f'Stopping {service_name}...')
            service.stop()
            stopped_services.append(service_name)
        except Exception as ex:
          logging.warning('Error: %s', ex)

        for service_name in stopped_services:
          self.poutput(f'Unregistering {service_name}...')
          self._dut.services.unregister(service_name)

        self._dut.adb.forward('--remove-all')


def load_current_workdir_cmd2_modules(c: BttcCmdApp):
  """Loads cmd2 modules from current working directory if any."""
  logging.debug('Searching local cmd2 module(s)...')
  for py_module in [
      f for f in os.listdir('.')
      if os.path.isfile(f) and f.endswith('_cli.py')]:
    py_module_path = os.path.join(os.getcwd(), py_module)
    load_cmd2_module(c, py_module_path)


def load_cmd2_module(c: BttcCmdApp, cmd2_module_path: str):
  """Loads Cmd2 module from given file path."""
  cmd2_module_name = pathlib.Path(cmd2_module_path).name
  local_module_name = f'local_cmd2.{cmd2_module_name}'
  spec = importlib.util.spec_from_file_location(
      local_module_name, cmd2_module_path)
  loaded_module = importlib.util.module_from_spec(spec)
  sys.modules[local_module_name] = loaded_module
  spec.loader.exec_module(loaded_module)
  loaded_cmd_set_cls_num = 0
  for cmd_set_cls in [
      cls for _, cls in inspect.getmembers(loaded_module, inspect.isclass)
      if issubclass(cls, cmd2.CommandSet)]:
    print(
        f'\t{Color.BOLD}Loaded customized cmd2 CommandSet: '
        f'{Color.UNDERLINE}{Color.CYAN}{cmd_set_cls}{Color.END}!')
    # CLASS_ATTR_DEFAULT_HELP_CATEGORY
    cmd_set_obj = cmd_set_cls(c)
    cmd_set_obj.__class__.CLASS_ATTR_DEFAULT_HELP_CATEGORY = 'hahaha'
    c.register_command_set(cmd_set_obj)
    loaded_cmd_set_cls_num += 1
  print(
      f'\t{Color.BOLD}===== Total {loaded_cmd_set_cls_num:,d}'
      f' cmd2 CommandSet found! ====={Color.END}\n\n')


def go(serial: str | None = None):
  """Enters Cli prompt."""
  c = BttcCmdApp(serial)
  load_current_workdir_cmd2_modules(c)
  c.cmdloop()
  c.free_dut()
  print('=' * 10 + f' {EXIST_MSG} ' + '=' * 10)
  print('')
  os._exit(0)


if __name__ == '__main__':
  args = select_parser.parse_args()
  # Remove command line argument to prevent Cmd2 mis-interpreting them.
  sys.argv = sys.argv[:1]
  go(args.serial)
