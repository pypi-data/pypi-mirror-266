# Copyright 2023 Iguazio
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
#

import pydantic


class AffectedResource(pydantic.BaseModel):
    """Affected resource."""

    type: str
    id_str: str
    id: int
    name: str


class ParametersText(pydantic.BaseModel):
    """Parameters text."""

    name: str
    value: str


class ParametersUint64(pydantic.BaseModel):
    """Parameters uint64."""

    name: str
    value: int
