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

import attrs
import dask.dataframe as dd

from tsum.coverage import coverage
from tsum.model import Pattern
from tsum.residue import residue
from tsum.saving import saving


def pattern_marshalling(S: set[Pattern], T: dd.DataFrame):
    patterns = set()
    remaining_patterns = set(S)

    while remaining_patterns:
        b_top = float("-inf")
        p_top = None
        residual_table = residue(S=patterns, T=T)

        for pattern in remaining_patterns:
            compression = saving(pattern=pattern, T=residual_table)

            if compression > b_top:
                b_top = compression
                p_top = pattern

        if b_top > 0:
            coverage_ = coverage(T=T, pattern=p_top)
            pattern = attrs.evolve(p_top, saving=b_top, coverage=coverage_)
            patterns.add(pattern)

        remaining_patterns.remove(p_top)

    return patterns
