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
from tsum.saving import saving


def expand(T: dd.DataFrame, pattern: Pattern) -> Pattern:
    all_attributes = set(T.columns)
    matched_attributes = set(pattern.pattern.keys())
    attributes = all_attributes - matched_attributes
    best_pattern = None
    highest_compression_saving = 0

    for attribute in attributes:
        values = T[attribute].unique()

        for value in values:
            new_pattern = pattern.with_new_pattern(pattern={attribute: value})
            compression_saving = saving(T=T, pattern=new_pattern)

            if compression_saving > highest_compression_saving:
                highest_compression_saving = compression_saving
                best_pattern = new_pattern

    if best_pattern and (
        saving(T=T, pattern=best_pattern) > saving(T=T, pattern=pattern)
    ):
        return expand(T=T, pattern=best_pattern)

    return pattern
