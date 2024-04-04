# Copyright 2024 Jetperch LLC
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

from joulescope_ui import register, CAPABILITIES, N_, register
from joulescope_ui.styles import styled_widget
from .manager import PluginManager
from .selector import PluginSelectorWidget
from joulescope_ui.widget_tools import CallableAction, CallableSlotAdapter, settings_action_create, context_menu_show


__all__ = [
    'register', 'styled_widget', 'CAPABILITIES', 'N_',
    'CallableAction', 'CallableSlotAdapter', 'settings_action_create', 'context_menu_show',
]
