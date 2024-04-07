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

import dask.dataframe as dd

from tsum.model import Pattern
from tsum.util import filter_, bits_for


def benefit(T: dd.DataFrame, pattern: Pattern) -> int:
    if not pattern.pattern:
        return 0

    attributes = list(pattern.pattern.keys())
    values = [pattern.pattern[attribute] for attribute in attributes]

    N = len(filter_(T=T, pattern=pattern))
    W = sum(bits_for(value) for value in values)

    return (N - 1) * W
