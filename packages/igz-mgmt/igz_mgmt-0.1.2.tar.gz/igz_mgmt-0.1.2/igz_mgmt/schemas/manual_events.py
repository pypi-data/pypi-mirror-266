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

import igz_mgmt.resources  # noqa: F401
import igz_mgmt.schemas.events

# for backwards compatibility, set classes from events
AffectedResource = igz_mgmt.schemas.events.AffectedResource
ParametersText = igz_mgmt.schemas.events.ParametersText
ParametersUint64 = igz_mgmt.schemas.events.ParametersUint64
ManualEventSchema = igz_mgmt.resources.Event
