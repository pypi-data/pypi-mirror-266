# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017-2023 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
'''Ddclaration of the Group role, i.e. its settings.

Needed for sharing of group role across ansar-group and ansar (network, etc).
'''

import ansar.create as ar
from .socketry import *
from .directory_if import *

__all__ = [
	'GroupSettings',
]

class GroupSettings(object):
	def __init__(self, connect_above=None, roles=None, main_role=None, forwarding=False,
		show_scopes=None, connect_scope=None, connect_file=None):
		self.connect_above = connect_above or HostPort()
		self.roles = roles
		self.main_role = main_role
		self.forwarding = forwarding
		self.show_scopes = show_scopes
		self.connect_scope = connect_scope
		self.connect_file = connect_file

GROUP_SETTINGS_SCHEMA = {
	'connect_above': ar.Any(),
	'roles': ar.Unicode(),
	'main_role': ar.Unicode(),
	'forwarding': ar.Boolean(),
	'show_scopes': ar.Boolean(),
	'connect_scope': ScopeOfService,
	'connect_file': ar.Unicode(),
}

ar.bind(GroupSettings, object_schema=GROUP_SETTINGS_SCHEMA)
