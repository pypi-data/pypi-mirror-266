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
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *

__all__ = [
	'ScopeOfService',
	'Published',
	'NotPublished',
	'Subscribed',
	'Available',
	'NotAvailable',
	'Delivered',
	'NotDelivered',
	'Clear',
	'Cleared',
	'Dropped',
	'NetworkEnquiry',
	'NetworkConnect',
	'DirectoryRoute',
	'DirectoryScope',
	'DirectoryAncestry',
]

# Build the local published/subscribed objects.
#
ScopeOfService = ar.Enumeration(PROCESS=1, GROUP=2, HOST=3, LAN=4, WAN=5)

#
#
class Published(object):
	def __init__(self, published_name=None, declared_scope=ScopeOfService.WAN, listening_ipp=None):
		self.published_name = published_name
		self.declared_scope = declared_scope
		self.listening_ipp = listening_ipp or HostPort()

class NotPublished(ar.Faulted):
	def __init__(self, requested_name=None, reason=None):
		self.requested_name = requested_name
		self.reason = reason
		ar.Faulted.__init__(self, f'cannot publish "{requested_name}"', reason)
		#self.condition = cannot
		#self.explanation = reason
		self.error_code = None
		self.error_text = None

class Subscribed(object):
	def __init__(self, subscribed_search=None, declared_scope=ScopeOfService.WAN):
		self.subscribed_search = subscribed_search
		self.declared_scope = declared_scope

# The actual service directory with listings and searches.
#

# Session messages to publish/listen controllers.
# Subscribe/client/calling/outbound end.
class Available(object):
	def __init__(self, key=None, agent_address=None):
		self.key = key
		self.agent_address = agent_address

class NotAvailable(ar.Faulted):
	def __init__(self, key=None, reason=None, agent_address=None):
		self.key = key
		self.reason = reason
		self.agent_address = agent_address
		ar.Faulted.__init__(self, 'no peer available', reason)
		#self.condition = cannot
		#self.explanation = reason
		self.error_code = None
		self.error_text = None

# Publish/service/answering/inbound end.
class Delivered(object):
	def __init__(self, key=None, agent_address=None):
		self.key = key
		self.agent_address = agent_address

class NotDelivered(ar.Faulted):
	def __init__(self, published_name=None, remote_address=None):
		self.published_name = published_name
		self.remote_address = remote_address
		ar.Faulted.__init__(self, 'no service to peer')
		#self.condition = cannot
		#self.explanation = reason
		self.error_code = None
		self.error_text = None

class Clear(object):
	def __init__(self, session=None, value=None):
		self.session = session
		self.value = value

class Cleared(object):
	def __init__(self, value=None):
		self.value = value

class Dropped(ar.Faulted):
	def __init__(self, reason=None):
		self.reason = reason
		ar.Faulted.__init__(self, 'established peer lost', reason)
		#self.condition = cannot
		#self.explanation = reason
		self.error_code = None
		self.error_text = None

ENDING_SCHEMA = {
	'session': ar.Any,
	'value': ar.Any,
	'reason': str,
	'condition': str,
	'explanation': str,
	'error_text': str,
	'error_code': ar.Integer8(),
	'exit_code': ar.Integer8(),
}

ar.bind(Clear, object_schema=ENDING_SCHEMA, copy_before_sending=False)
ar.bind(Cleared, object_schema=ENDING_SCHEMA, copy_before_sending=False)
ar.bind(Dropped, object_schema=ENDING_SCHEMA, copy_before_sending=False)

SHARED_SCHEMA = {
	#'key': ar.VectorOf(ar.Integer8()),
	'key': str,
	'name': str,
	'requested_name': str,
	'requested_search': str,
	'published_name': str,
	'subscribed_search': str,
	'published_name': str,
	'remote_address': ar.Address(),
	'session_address': ar.Address(),
	'declared_scope': ScopeOfService,
	'service_scope': ScopeOfService,
	'reason': ar.String(),
	'listening_ipp': ar.UserDefined(HostPort),
	'connecting_ipp': ar.UserDefined(HostPort),
	'parent_ipp': ar.UserDefined(HostPort),
	'child_ipp': ar.UserDefined(HostPort),
	'subscription': ar.UserDefined(Subscribed),
	'agent_address': ar.Address(),
	'address': ar.Address(),
}

SHARED_SCHEMA.update(ENDING_SCHEMA)

ar.bind(Subscribed, object_schema=SHARED_SCHEMA)
ar.bind(Published, object_schema=SHARED_SCHEMA)
ar.bind(Available, object_schema=SHARED_SCHEMA)
ar.bind(NotAvailable, object_schema=SHARED_SCHEMA)
ar.bind(Delivered, object_schema=SHARED_SCHEMA)
ar.bind(NotDelivered, object_schema=SHARED_SCHEMA)

# matched[key] = a (address of ServiceRoute)
# and
# key added to each find and listing set
# self.directory[service_name] = [message, set()]
# self.find[k] = [message, set(), dfa]
# where k =
# f'{subscriber_address}/{requested_search}'
class DirectoryRoute(object):
	def __init__(self, search_or_listing=None, agent_address=None, route_key=None):
		self.search_or_listing = search_or_listing
		self.agent_address = agent_address
		self.route_key = route_key or ar.default_set()

DIRECTORY_ROUTE_SCHEMA = {
	'search_or_listing': ar.Unicode(),
	'agent_address': ar.Address(),
	'route_key': ar.SetOf(ar.Unicode()),
}

ar.bind(DirectoryRoute, object_schema=DIRECTORY_ROUTE_SCHEMA)

class DirectoryScope(object):
	def __init__(self, scope=None, connect_above=None, started=None, connected=None, not_connected=None,
			listing=None, find=None, accepted=None):
		self.scope = scope
		self.connect_above = connect_above or HostPort()
		self.started = started
		self.connected = connected
		self.not_connected = not_connected
		self.listing = listing or ar.default_vector()
		self.find = find or ar.default_vector()
		self.accepted = accepted or ar.default_vector()

DIRECTORY_SCOPE_SCHEMA = {
	'scope' : ScopeOfService,
	'connect_above': ar.Any(),
	'started': ar.WorldTime(),
	'connected': ar.WorldTime(),
	'not_connected': ar.Unicode(),
	'listing': ar.VectorOf(ar.UserDefined(DirectoryRoute)),
	'find': ar.VectorOf(ar.UserDefined(DirectoryRoute)),
	'accepted': ar.VectorOf(ar.UserDefined(HostPort)),
}

ar.bind(DirectoryScope, object_schema=DIRECTORY_SCOPE_SCHEMA)

#
#
class NetworkEnquiry(object):
	def __init__(self, lineage=None):
		self.lineage = lineage or ar.default_vector()

NETWORK_ENQUIRY_SCHEMA = {
	'lineage': ar.VectorOf(DirectoryScope),
}

ar.bind(NetworkEnquiry, object_schema=NETWORK_ENQUIRY_SCHEMA)

#
#
class NetworkConnect(object):
	def __init__(self, scope=None, connect_above=None):
		self.scope = scope
		self.connect_above = connect_above

NETWORK_CONNECT_SCHEMA = {
	'scope': ScopeOfService,
	'connect_above': ar.Any(),
}

ar.bind(NetworkConnect, object_schema=NETWORK_CONNECT_SCHEMA)

#
#
class DirectoryAncestry(object):
	def __init__(self, lineage=None):
		self.lineage = lineage or ar.default_vector()

DIRECTORY_ANCESTRY_SCHEMA = {
	'lineage': ar.VectorOf(DirectoryScope),
}

ar.bind(DirectoryAncestry, object_schema=DIRECTORY_ANCESTRY_SCHEMA)
