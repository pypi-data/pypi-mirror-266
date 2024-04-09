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

"""Entry point of BTTC Cli."""

from bttc.cli import constants
import cmd2
from typing import (
    Callable,
    Type,
)


CommandSet = cmd2.CommandSet
Color = constants.Color


def with_default_category(
    category: str, *, heritable: bool = True) -> Callable[
        [Type['CommandSet']], Type['CommandSet']]:
    """
    Decorator that applies a category to all ``do_*`` command methods in a class
    that do not already have a category specified.

    CommandSets that are decorated by this with `heritable` set to True
    (default) will set a class attribute that is inherited by all subclasses
    unless overridden. All commands of this CommandSet and all subclasses of
    this CommandSet that do not declare an explicit category will be placed in
    this category. Subclasses may use this decorator to override the default
    category.

    If `heritable` is set to False, then only the commands declared locally to
    this CommandSet will be placed in the specified category. Dynamically
    created commands, and commands declared in sub-classes will not receive this
    category.

    Args:
      category: category to put all uncategorized commands in
      heritable: Flag whether this default category should apply to sub-classes.
          Defaults to True

    Returns:
      Decorator function
    """
    customized_category = (
        f'{Color.BOLD}{Color.PURPLE}>>> {category} <<<{Color.END}')

    return cmd2.with_default_category(
        category=customized_category, heritable=heritable)
