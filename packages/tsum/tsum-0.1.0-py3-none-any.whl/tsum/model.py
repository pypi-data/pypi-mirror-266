# Copyright 2024 Fasih Khatib
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any

import attr
import attrs
from frozendict import frozendict


@attr.define(frozen=True, auto_attribs=True)
class Pattern:
    pattern: frozendict = attr.ib(default=frozendict())
    saving: float = attr.ib(default=0.0)
    coverage: float = attr.ib(default=0.0)

    @property
    def empty(self):
        return len(self.pattern) == 0

    def with_new_pattern(self, pattern: dict[Any, Any]) -> "Pattern":
        pattern = frozendict({**self.pattern, **pattern})
        return attrs.evolve(self, pattern=pattern)
