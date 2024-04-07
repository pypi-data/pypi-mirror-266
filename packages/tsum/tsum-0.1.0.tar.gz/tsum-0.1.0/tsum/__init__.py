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
from .local_expansion import local_expansion
from .model import Pattern
from .pattern_marshalling import pattern_marshalling


def summarize(ddf: dd.DataFrame) -> list[Pattern]:
    patterns = local_expansion(T=ddf)
    return pattern_marshalling(S=set(patterns), T=ddf)
