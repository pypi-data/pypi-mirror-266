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

import uuid
import re
import ansar.create as ar
from .socketry import *
from .transporting import *
from .plumbing import *
from .wan import *
from .product import *
from .networking_if import *
from .directory_if import *
from .connect_directory import *

__all__ = [
	'pb',
	'find_overlap',
	'publish',
	'subscribe',
	'retract',
	'clear',
	'key_service',
	'ServiceDirectory',
]

# All the distinct machine states used by this
# module.
class INITIAL: pass
class NORMAL: pass
class OPENING: pass
class PENDING: pass
class READY: pass
class CLEARING: pass
class GLARING: pass
class CLOSING: pass
class COMPLETING: pass
class RELAYING: pass

class LOOPING: pass
class LATCHING: pass
class LOOPED: pass

class CONNECTION_PEERING: pass
class CONNECTION_LOOPING: pass
class CONNECTION_LATCHING: pass
class CONNECTION_LOOPED: pass
class RELAY_PEERING: pass
class RELAY_LOOPING: pass
class RELAY_LATCHING: pass
class RELAY_LOOPED: pass

class CONNECTING: pass
class CONNECTED: pass

#
#
def ipp_key(ipp):
	return str(ipp)

def find_overlap(table, address):
	a = address[-1]
	for k, v in table.items():
		if k[-1] == a:
			return k, v
	return None, None

# directory ... names and lookups and addresses relating to both
# sockets ..... dedicated sockets engine
# channel ..... back channel to sockets
# house ....... container of listen/connect service controllers.
pb = ar.Gas(directory=None, sockets=None, channel=None, house=None)

def create_directory(root):
	# Directory created in node_vector()
	# but stopped below.
	pb.sockets = root.create(SocketSelect)
	pb.channel = root.select(SocketChannel)
	pb.house = root.create(PubSub)

def stop_directory(root):
	root.send(ar.Stop(), pb.house)
	root.select(ar.Completed)
	pb.channel.send(ar.Stop(), root.address)
	root.select(ar.Completed)
	# Stop the directory started by
	# node_vector().
	if pb.directory is not None:
		root.send(ar.Stop(), pb.directory)
		# NOTE!
		# The root object did not create this
		# object so normal completion cannot be
		# used. The directory object is specifically
		# coded to respond to Stop with an Ack. As
		# well as completing.
		root.select(ar.Ack, seconds=5.0)

ar.AddOn(create_directory, stop_directory)

# Private communications from the pub-sub api (i.e. ar.publish()) to
# the operational machinery.
class PublishAsName(object):
	def __init__(self, requested_name=None, create_session=None, declared_scope=ScopeOfService.WAN):
		self.requested_name = requested_name
		self.create_session = create_session
		self.declared_scope = declared_scope

class SubscribeToName(object):
	def __init__(self, requested_search=None, create_session=None, declared_scope=ScopeOfService.WAN):
		self.requested_search = requested_search
		self.create_session = create_session
		self.declared_scope = declared_scope

class Retract(object):
	def __init__(self, address=None):
		self.address = address

# Private communications within the directory hierarchy, e.g. ServiceListing is sent from
# the PublishingAgent to the local directory and is then passed up the chain of directories.
class ServiceListing(object):
	def __init__(self, requested_name=None, agent_address=None, declared_scope=ScopeOfService.WAN, listing_id=None, listening_ipp=None, connecting_ipp=None):
		self.requested_name = requested_name
		self.agent_address = agent_address
		self.declared_scope = declared_scope
		self.listing_id = listing_id
		self.listening_ipp = listening_ipp or HostPort()
		self.connecting_ipp = connecting_ipp or HostPort()

class FindService(object):
	def __init__(self, requested_search=None, agent_address=None, declared_scope=ScopeOfService.WAN):
		self.requested_search = requested_search
		self.agent_address = agent_address
		self.declared_scope = declared_scope

class PushedDirectory(object):
	def __init__(self, listing=None, find=None):
		self.listing = listing
		self.find = find

	def empty(self):
		if len(self.listing) == 0 and len(self.find) == 0:
			return True
		return False

class UnlistService(object):
	def __init__(self, requested_name=None, agent_address=None, declared_scope=None):
		self.requested_name = requested_name
		self.agent_address = agent_address
		self.declared_scope = declared_scope

class UnlistFind(object):
	def __init__(self, subscribed_search=None, agent_address=None, declared_scope=None):
		self.subscribed_search = subscribed_search
		self.agent_address = agent_address
		self.declared_scope = declared_scope

class TrimRoutes(object):
	def __init__(self, address=None):
		self.address = address

class CapRoutes(object):
	def __init__(self, service_scope=None):
		self.service_scope = service_scope

class RetractRoute(object):
	def __init__(self, key=None):
		self.key = key

SHARED_SCHEMA = {
	#'key': ar.VectorOf(ar.Integer8()),
	'key': str,
	'requested_name': str,
	'requested_search': str,
	'subscribed_search': str,
	'declared_scope': ScopeOfService,
	'listing_id': ar.UUID(),
	'service_scope': ScopeOfService,
	'create_session': ar.Type(),
	'listening_ipp': ar.UserDefined(HostPort),
	'connecting_ipp': ar.UserDefined(HostPort),
	'parent_ipp': ar.UserDefined(HostPort),
	'child_ipp': ar.UserDefined(HostPort),
	'agent_address': ar.Address(),
	'address': ar.Address(),
}

ar.bind(PublishAsName, object_schema=SHARED_SCHEMA)
ar.bind(SubscribeToName, object_schema=SHARED_SCHEMA)
ar.bind(Retract, object_schema=SHARED_SCHEMA)

ar.bind(ServiceListing, object_schema=SHARED_SCHEMA)
ar.bind(FindService, object_schema=SHARED_SCHEMA)
ar.bind(UnlistService, object_schema=SHARED_SCHEMA)
ar.bind(UnlistFind, object_schema=SHARED_SCHEMA)
ar.bind(TrimRoutes, object_schema=SHARED_SCHEMA)
ar.bind(CapRoutes, object_schema=SHARED_SCHEMA)
ar.bind(RetractRoute, object_schema=SHARED_SCHEMA)

COPY_SCHEMA = {
	'listing': ar.VectorOf(ar.UserDefined(ServiceListing)),
	'find': ar.VectorOf(ar.UserDefined(FindService)),
}

ar.bind(PushedDirectory, object_schema=COPY_SCHEMA)

def address_to_text(a):
	t = ','.join([f'{i:x}' for i in a])
	return t

# This is the object that owns and manages the routing between
# a subscriber and a service. It is created on a match and
# updates the two parties as needed. Routes are fairly static.
# They are only affected by changes to the directory tree. Routes
# are the basis for sessions. The session abstraction is in the
# SubscriptionAgent object using "loop" messages to establish
# a "subscriber loop" to a remote end over dedicated transports,
# i.e. not the same transports used by the directory tree.
class ServiceRoute(ar.Point, ar.StateMachine):
	def __init__(self, key, find_address, listing_address, connection):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.key = key
		self.find_address = find_address
		self.listing_address = listing_address
		self.connection = connection

def ServiceRoute_INITIAL_Start(self, message):
	if isinstance(self.connection, ServiceByRelay):
		relay_id = uuid.uuid4()
		self.send(RelayLookup(relay_id=relay_id), self.connection.relay_address)
		self.start(ar.T1, 5.0)
		return RELAYING
	outbound = self.connection.outbound(self.key)
	inbound = self.connection.inbound(self.key)

	out_type = outbound.__art__.name
	in_type = inbound.__art__.name

	out_address = address_to_text(self.find_address)
	in_address = address_to_text(self.listing_address)

	self.trace(f'Match sends "{out_type}" to [{out_address}]')
	self.trace(f'And "{in_type}" to [{in_address}]')

	self.send(outbound, self.find_address)
	self.send(inbound, self.listing_address)
	return NORMAL

def ServiceRoute_RELAYING_RelayRedirect(self, message):
	self.connection.redirect = message
	outbound = self.connection.outbound(self.key)
	inbound = self.connection.inbound(self.key)

	out_type = outbound.__art__.name
	in_type = inbound.__art__.name

	out_address = address_to_text(self.find_address)
	in_address = address_to_text(self.listing_address)

	self.trace(f'Match sends "{out_type}" to [{out_address}]')
	self.trace(f'And "{in_type}" to [{in_address}]')

	self.send(outbound, self.find_address)
	self.send(inbound, self.listing_address)
	return NORMAL

def ServiceRoute_RELAYING_T1(self, message):
	out_address = address_to_text(self.find_address)
	in_address = address_to_text(self.listing_address)

	self.trace(f'Failed relay from [{out_address}] to [{in_address}]')
	self.complete(ar.Aborted())

def ServiceRoute_NORMAL_Stop(self, message):
	out_address = address_to_text(self.find_address)
	in_address = address_to_text(self.listing_address)

	self.trace(f'Match sends RetractRoute to [{out_address}] and [{in_address}] and completes')
	
	self.send(RetractRoute(self.key), self.find_address)
	self.send(RetractRoute(self.key), self.listing_address)
	self.complete(ar.Aborted())

SERVICE_ROUTE_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RELAYING: (
		(RelayRedirect, ar.T1), ()
	),
	NORMAL: (
		(ar.Stop,), ()
	),
}

ar.bind(ServiceRoute, SERVICE_ROUTE_DISPATCH)

# Messages from match object (ServiceRoute) to the two different
# ends of the relation. The PublishingAgent and SubscriptionAgent objects
# will receive and initiate "calls" based on these messages.
class RouteToAddress(object):
	def __init__(self, scope=None, address=None, key=None):
		self.scope = scope
		self.address = address
		self.key = key

class InboundFromAddress(object):
	def __init__(self, scope=None, address=None, key=None):
		self.scope = scope
		self.address = address
		self.key = key

class RouteOverConnected(object):
	def __init__(self, scope=None, connecting_ipp=None, key=None):
		self.scope = scope
		self.connecting_ipp = connecting_ipp or HostPort()
		self.key = key

class InboundOverAccepted(object):
	def __init__(self, scope=None, key=None):
		self.scope = scope
		self.key = key

class RouteByRelay():
	def __init__(self, scope=None, redirect=None, key=None):
		self.scope = scope
		self.redirect = redirect or RelayRedirect()
		self.key = key

class InboundByRelay():
	def __init__(self, scope=None, redirect=None, key=None):
		self.scope = scope
		self.redirect = redirect or RelayRedirect()
		self.key = key

IO_SCHEMA = {
	'address': ar.Address(),
	'key': str,
	'name': str,
	'connecting_ipp': ar.UserDefined(HostPort),
	'scope': ScopeOfService,
	'redirect': ar.UserDefined(RelayRedirect),
}

ar.bind(RouteToAddress, object_schema=IO_SCHEMA)
ar.bind(InboundFromAddress, object_schema=IO_SCHEMA)
ar.bind(RouteOverConnected, object_schema=IO_SCHEMA)
ar.bind(InboundOverAccepted, object_schema=IO_SCHEMA)
ar.bind(RouteByRelay, object_schema=IO_SCHEMA)
ar.bind(InboundByRelay, object_schema=IO_SCHEMA)

#
#
class OpenPeer(object):
	def __init__(self, connecting_ipp=None, key=None):
		self.connecting_ipp = connecting_ipp or HostPort()
		self.key = key

class PeerOpened(object):
	def __init__(self, connecting_ipp=None, key=None):
		self.connecting_ipp = connecting_ipp or HostPort()
		self.key = key

class NotPeered(object):
	def __init__(self, key=None, reason=None, connecting_ipp=None):
		self.key = key
		self.reason = reason
		self.connecting_ipp = connecting_ipp or HostPort()

class PeerLost(object):
	def __init__(self, connecting_ipp=None, key=None):
		self.connecting_ipp = connecting_ipp or HostPort()
		self.key = key

class ClosePeer(object):
	def __init__(self, connecting_ipp=None, key=None):
		self.connecting_ipp = connecting_ipp or HostPort()
		self.key = key

PEER_SCHEMA = {
	'connecting_ipp': ar.UserDefined(HostPort),
	'key': str,
	'reason': str,
}

ar.bind(OpenPeer, object_schema=PEER_SCHEMA)
ar.bind(PeerOpened, object_schema=PEER_SCHEMA)
ar.bind(NotPeered, object_schema=PEER_SCHEMA)
ar.bind(PeerLost, object_schema=PEER_SCHEMA)
ar.bind(ClosePeer, object_schema=PEER_SCHEMA)

# Objects that capture the requirements for 3 different methods
# of connection between subscriber and publisher.
class DirectService(object):
	def __init__(self, find, listing):
		self.find = find
		self.listing = listing

	def outbound(self, key):
		return RouteToAddress(ScopeOfService.PROCESS, self.listing.agent_address, key)

	def inbound(self, key):
		return InboundFromAddress(ScopeOfService.PROCESS, self.find.agent_address, key)

# Between two objects needing a TCP connection from
# subscribing process to publishing process. Listening
# address needs tuning based on whether its intra-host
# or across a LAN.
class ServiceOverConnection(object):
	def __init__(self, scope, find, listing):
		self.scope = scope
		self.find = find
		self.listing = listing

	def outbound(self, key):
		return RouteOverConnected(self.scope, self.listing.connecting_ipp, key)

	def inbound(self, key):
		return InboundOverAccepted(self.scope, key)

# The extra step needed for relay setup. A query/response
# needed with the relay manager before the connection
# messages can be sent to the ends of the call.
class ServiceByRelay(object):
	def __init__(self, finding, listing, relay_address):
		self.relay_address = relay_address
		self.redirect = None

	def outbound(self, key):
		return RouteByRelay(ScopeOfService.WAN, self.redirect, key)

	def inbound(self, key):
		return InboundByRelay(ScopeOfService.WAN, self.redirect, key)

# The per-process part of the distributed name service.
# Accepts local listings and searches and creates matches.
# Receives listings and searches from below as well. All
# information forwarded to next level up.
def key_service(key):
	try:
		i = key.index(':')
	except ValueError:
		return None
	return key[i + 1:]

def key_id(key):
	try:
		a = key.index('@')
		c = key.index(':')
	except ValueError:
		return None
	return key[a + 1:c]

def id_connection(kid):
	try:
		a = kid.index('(')
		c = kid.index(')')
	except ValueError:
		return None
	return kid[a + 1:c]

def id_process(kid):
	try:
		a = kid.index(')')
	except ValueError:
		return None
	return kid[a + 1:]

def overlapping_route(a, b):
	ra = reversed(a)
	rb = reversed(b)
	for x, y in zip(ra, rb):
		if x != y:
			return False
	return True

CONNECT_ABOVE = 'connect-above'
ACCEPT_BELOW = 'accept-below'

class ServiceDirectory(ar.Threaded, ar.StateMachine):
	def __init__(self, scope=None, connect_above=None, accept_below=None):
		ar.Threaded.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.scope = scope or ScopeOfService.PROCESS
		self.connect_above = connect_above
		self.accept_below = accept_below or HostPort()
		self.ctd = None
		self.directory = {}
		self.find = {}
		self.matched = {}
		self.connected_up = None
		self.not_connected = None
		self.connected = None
		self.listening = None
		self.accepted = {}
		self.started = None
		self.stopped = None
		self.reconnecting = None

	def found(self, service_name, f, d):
		find = f[0]
		listing = d[0]
		find_address = find.agent_address
		find_matched = f[1]
		listing_address = listing.agent_address
		listing_id = listing.listing_id
		listing_matched = d[1]

		# As well as being unique within this directory the
		# connection engine in the subscriber agent relies on
		# content and layout of this key. Refer to
		# key_service(), key_id(), etc.
		who = address_to_text(find_address)
		key = f'{who}@{listing_address}{listing_id}:{listing.requested_name}'

		if key in self.matched:
			self.warning(f'Duplicate find/service match [{ScopeOfService.to_name(self.scope)}] "{key}"')
			return
		self.trace(f'Adds route [{ScopeOfService.to_name(self.scope)}] "{key}"')

		# Everything lines up - we have a relation. Connection details
		# are dependent on where this directory is running.
		if self.scope == ScopeOfService.PROCESS:
			a = self.create(ServiceRoute, key, find_address, listing_address, DirectService(find, listing))
		elif self.scope in (ScopeOfService.GROUP, ScopeOfService.HOST, ScopeOfService.LAN):
			a = self.create(ServiceRoute, key, find_address, listing_address, ServiceOverConnection(self.scope, find, listing))
		elif self.scope == ScopeOfService.WAN:
			a = self.create(ServiceRoute, key, find_address, listing_address, ServiceByRelay(find, listing, self.parent_address))
		else:
			self.warning(f'Directory at unknown scope "{self.scope}"')
		self.assign(a, key)
		self.matched[key] = a
		find_matched.add(key)
		listing_matched.add(key)

	def conclude_host(self, address, message):
		"""Determine a host address suitable for connection.

		Combine the network info accumulated for accepted connections
		and the information offered in a service listing to resolve
		the most appropriate host address to use for connection. Most
		significantly this means overlaying an "IP any" address with
		the address of the remote host available at the moment of
		accepting. This will resolve to either a local host (127.x)
		or LAN address (e.g. 192.x) as the calling process gets
		further away from the offering. That info is then sent to
		processes below this directory that will know the service
		host by the same address as this process remembers accepting
		from.
		"""
		r, a = find_overlap(self.accepted, address)
		if r is None:
			self.warning(f'Cannot resolve connection address for {message.requested_name} - no record of accepting')
			message.connecting_ipp.host = None
			return
		if message.listening_ipp.host == '0.0.0.0':
			message.connecting_ipp.host = a.accepted_ipp.host
		else:
			message.connecting_ipp.host = message.listening_ipp.host
		message.connecting_ipp.port = message.listening_ipp.port

	### PS-pub-10 Directory installs a new service.
	def add_listing(self, message):
		service_name = message.requested_name

		d = self.directory.get(service_name, None)
		if d is None:
			d = [message, set()]
			self.directory[service_name] = d
			self.trace(f'Added listing "{service_name}"')
		else:
			self.warning(f'Duplicate listing for "{service_name}"')
			d[0] = message

		# Match listing to finds.
		for _, f in self.find.items():
			dfa = f[2]
			m = dfa.match(service_name)
			if m:
				### PS-pub-10 New service matches existing search.
				self.found(service_name, f, d)

		return

		# Not duplicates - yet.
		if service_name in self.directory:
			self.warning(f'Duplicate listing for "{service_name}"')
			return

		# Add service to table
		d = [message, set()]
		self.directory[service_name] = d
		self.trace(f'Added listing "{service_name}"')

		# Match listing to finds.
		for _, f in self.find.items():
			dfa = f[2]
			m = dfa.match(service_name)
			if m:
				### PS-pub-10 New service matches existing search.
				self.found(service_name, f, d)

	### PS-sub-9 Directory installs a new search.
	def add_find(self, message):
		find_name = message.requested_search
		find_address = message.agent_address

		jf = address_to_text(find_address)
		k = f'{jf}/{find_name}'
		if k in self.find:
			self.warning(f'Duplicate find for "{k}"')
			return

		try:
			dfa = re.compile(find_name)
		except re.error as e:
			self.warning(f'Cannot compile expression "{e.msg}"')
			return

		# Add client to table
		f = [message, set(), dfa]
		self.find[k] = f
		self.trace(f'Added search "{k}"')

		# Match find to listings.
		for service_name, d in self.directory.items():
			m = dfa.match(service_name)
			if m:
				### PS-sub-9 New find matches existing service.
				self.found(service_name, f, d)

	def remove_listing(self, message):
		service_name = message.requested_name

		# Remove the entry and terminate any routes that
		# were based on its existence.
		# d = [message, set()]
		d = self.directory.pop(service_name, None)
		if d is None:
			self.warning(f'Unknown service listing for "{service_name}"')
			return
		self.trace(f'Removed listing "{service_name}" ({len(d[1])} matches to stop)')
		
		for k in d[1]:
			a = self.matched.get(k, None)
			if a:
				self.send(ar.Stop(), a)

	def remove_find(self, message):
		find_name = message.subscribed_search
		find_address = message.agent_address

		jf = address_to_text(find_address)
		k = f'{jf}/{find_name}'

		# Remove the entry and terminate any routes that
		# were based on its existence.
		# f = [message, set()]
		f = self.find.pop(k, None)
		if f is None:
			self.warning(f'Unknown find listing for {k}')
			return
		self.trace(f'Removed find "{k}" ({len(f[1])} matches to stop)')
		
		for k in f[1]:
			a = self.matched.get(k, None)
			if a:
				self.send(ar.Stop(), a)

	def top_of_directory(self):
		listing = [v[0] for k, v in self.directory.items() if v[0].declared_scope > self.scope]
		find = [v[0] for k, v in self.find.items() if v[0].declared_scope > self.scope]
		return PushedDirectory(listing, find)

	# self.directory[service_name] = [FindService, set()]
	# self.find[search_key] = [FindService, set()]
	#
	# All the finds that matched to a service.
	# for k in self.find[search_key][1]:
	#	a = self.match[k]
	#	self.send(Stop(), a)

	# All the services matched to a find.
	# for k in self.find[search_key][1]:
	#	a = self.match[k]
	#	self.send(Stop(), a)

	def lost_below(self, lost):
		# All those ServiceRoutes that are compromised by a missing
		# publisher or subscriber.
		broken = set()

		# Keys of those find/directory entries that can no longer
		# be reached due to loss of accepted.
		removing = set()
		for k, f in self.find.items():
			if overlapping_route(lost, f[0].agent_address):
				removing.add(k)
				broken.update(f[1])

		self.trace(f'Removing {len(removing)} subscriptions')		
		for r in removing:
			self.find.pop(r)

		removing = set()
		for k, d in self.directory.items():
			if overlapping_route(lost, d[0].agent_address):
				removing.add(k)
				broken.update(d[1])
				
		self.trace(f'Removing {len(removing)} publications')		
		for r in removing:
			self.directory.pop(r)

		for b in broken:
			a = self.matched.get(b, None)
			if a:
				self.send(ar.Stop(), a)

		if self.connected_up:
			self.send(TrimRoutes(lost), self.connected_up)

	def lost_above(self):
		self.connected_up = None
		lost = CapRoutes(self.scope)

		self.send(lost, self.address)

def settings_property_default(a, p, d):
	# Ugly but without this type-specific handling this
	# "generic" function wouldnt work for HostPorts.
	if isinstance(a, WideAreaAccess):
		empty = a.access_ipp.host is None
	elif isinstance(a, HostPort):
		empty = a.host is None
	else:
		empty = a is None

	if empty:
		# Plucking a value out of the Homebase object that
		# may not be there, e.g. running as a tool.
		if p is None or p[2] is None:
			return d
		return p[2]
	return a

def ServiceDirectory_INITIAL_Start(self, message):
	self.started = ar.world_now()

	self.trace(f'Scope of {ScopeOfService.to_name(self.scope)}')
	self.trace(f'Connecting up to "{ar.tof(self.connect_above)}"')
	self.trace(f'Listening below at "{ar.tof(self.accept_below)}"')

	self.ctd = self.create(ConnectToDirectory, self.connect_above)
	self.assign(self.ctd, CONNECT_ABOVE)

	# Acceptance of connections from lower directories.
	if isinstance(self.accept_below, HostPort):
		if self.accept_below.host is None:
			self.send(HostPort(host=None), self.parent_address)
		else:
			listen(self, self.accept_below, tag='directory-accept')
			return OPENING
	else:
		pass	# Acceptance arranged externally. May be a
				# Listening object for diagnosis.

	return NORMAL

def ServiceDirectory_OPENING_Listening(self, message):
	self.send(message.listening_ipp, self.parent_address)
	self.listening = message
	return NORMAL

def ServiceDirectory_OPENING_NotListening(self, message):
	f = ar.Failed(directory_listen=(message.error_text, 'directory cannot accept sub-directories'))
	self.complete(f)

def ServiceDirectory_OPENING_Accepted(self, message):
	# Using tail as the key ensures it works for
	# any object at the end of this proxy.
	self.accepted[self.return_address] = message
	return NORMAL

def ServiceDirectory_OPENING_Abandoned(self, message):
	# Using tail as the key ensures it works for
	# any object at the end of this proxy.
	r, a = find_overlap(self.accepted, self.return_address)
	if r is None:
		self.warning(f'Abandoned by unknown client')
		return NORMAL
	self.accepted.pop(r, None)
	return NORMAL

def ServiceDirectory_OPENING_Stop(self, message):
	self.stopped = self.return_address
	self.send(ar.Ack(), self.stopped)
	self.complete(ar.Aborted())

def ServiceDirectory_NORMAL_UseAddress(self, message):
	self.not_connected = None
	if self.connected_up is None:
		self.connected_up = message.address
		c = self.top_of_directory()
		if not c.empty():
			self.send(c, self.connected_up)
		self.not_connected = None
		self.connected = ar.world_now()
	else:
		self.warning(f'Connected when already connected')
	return NORMAL

def ServiceDirectory_NORMAL_NoAddress(self, message):
	if self.connected_up is not None:
		# Abnormal sockets failure. Connection to upper
		# levels should terminate with an Abandoned message.
		# This is a sockets fault on established transport.
		self.lost_above()
	return NORMAL

def ServiceDirectory_NORMAL_Listening(self, message):
	if self.listening is not None:
		self.warning('Listening and already doing so')
	self.listening = message
	return NORMAL

def ServiceDirectory_NORMAL_NotListening(self, message):
	if self.listening is None:
		self.warning('Not listening and already not doing so')
	self.listening = None
	# Done in the separate machine.
	#self.start(ar.T2, 10.0)
	return NORMAL

def ServiceDirectory_NORMAL_Accepted(self, message):
	# Using tail as the key ensures it works for
	# any object at the end of this proxy.
	self.accepted[self.return_address] = message
	return NORMAL

def ServiceDirectory_NORMAL_Abandoned(self, message):
	# Close/abandon of upward connection now handled
	# by the ConnectService object and mapped to ServiceDown

	self.lost_below(self.return_address)
	r, a = find_overlap(self.accepted, self.return_address)
	if r is None:
		self.warning(f'Abandoned by unknown client')
		return NORMAL
	self.accepted.pop(r, None)
	return NORMAL

def ServiceDirectory_NORMAL_Closed(self, message):
	return ServiceDirectory_NORMAL_Abandoned(self, message)

def ServiceDirectory_NORMAL_T2(self, message):
	# TBC - should be a repeat of INITIAL_Start handling
	# or nothing at all, i.e. handled by separate machine.
	if isinstance(self.accept_below, HostPort) and self.accept_below.host:
		listen(self, self.accept_below)
	return NORMAL

def ServiceDirectory_NORMAL_NotConnected(self, message):
	self.not_connected = message
	return NORMAL

def ServiceDirectory_NORMAL_PushedDirectory(self, message):
	nl = len(message.listing)
	nf = len(message.find)

	self.trace(f'Pushed "{nl}" listings and "{nf}" finds')

	for s in message.listing:
		# Suppress those listings at lower levels.
		if s.declared_scope < self.scope:
			continue
		# Patch the connecting ipp for those scenarios involving
		# a secondary connection, i.e. a peer.
		if self.scope in (ScopeOfService.GROUP, ScopeOfService.HOST, ScopeOfService.LAN):
			self.conclude_host(self.return_address, s)

		self.add_listing(s)

	for f in message.find:
		# Suppress those listings at lower levels.
		if f.declared_scope < self.scope:
			continue
		self.add_find(f)

	if self.connected_up:
		self.send(message, self.connected_up)
	return NORMAL

### PS-pub-9 Directory accepts listing.
def ServiceDirectory_NORMAL_ServiceListing(self, message):
	# Suppress those listings at lower levels.
	if message.declared_scope < self.scope:
		return NORMAL
	if self.scope in (ScopeOfService.GROUP, ScopeOfService.HOST, ScopeOfService.LAN):
		### PS-pub-9 Directory patches listing IP-port.
		self.conclude_host(self.return_address, message)
	self.add_listing(message)

	### PS-pub-9 Directory propagates listing.
	if self.connected_up and message.declared_scope > self.scope:
		self.send(message, self.connected_up)
	return NORMAL

### PS-sub-8 Directory accepts find.
def ServiceDirectory_NORMAL_FindService(self, message):
	# Suppress those listings at lower levels.
	if message.declared_scope < self.scope:
		return NORMAL
	self.add_find(message)

	### PS-sub-8 Directory propagates find.
	if self.connected_up and message.declared_scope > self.scope:
		self.send(message, self.connected_up)
	return NORMAL

def ServiceDirectory_NORMAL_UnlistService(self, message):
	# Suppress those listings at lower levels.
	if message.declared_scope < self.scope:
		return NORMAL
	self.remove_listing(message)
	if self.connected_up and message.declared_scope > self.scope:
		self.send(message, self.connected_up)
	return NORMAL

def ServiceDirectory_NORMAL_UnlistFind(self, message):
	# Suppress those listings at lower levels.
	if message.declared_scope < self.scope:
		return NORMAL
	self.remove_find(message)
	if self.connected_up and message.declared_scope > self.scope:
		self.send(message, self.connected_up)
	return NORMAL

def ServiceDirectory_NORMAL_CapRoutes(self, message):
	self.forward(message, pb.house, self.return_address)

	self.trace(f'Broadcasting cap to {len(self.accepted)} sub-directories')
	for a in self.accepted.values():
		self.send(message, a.remote_address)
	return NORMAL

def ServiceDirectory_NORMAL_TrimRoutes(self, message):
	self.lost_below(message.address)
	return NORMAL

# COMPLETE OUTPUT
# SCOPE | ADDRESS (METHOD) | STARTED (SPAN) | CONNECTED (SPAN) | PUB-SUB (listings, searches, connections)
# WAN some.dns.name: 32177 (ansar org, super-duper) - 2024-03-01T10:22:17 (32d) - (17/3/43)
# LAN 192.168.1.176: 32177 (super-duper/demo/mr-ansar) - 2024-03-01T10:22:17 (32d) -  (4/2/16)
# HOST 127.0.0.1: 32177 (static IP-port) - 2024-03-01T10:22:17 (32d) - (0/2/4)
# GROUP 127.0.0.1:43301 (ephemeral IP-port) - 2024-03-01T10:22:17 (32d) - (0/2/2)

# OR ...
# NOT CONNECTED some.dns.name: 32177 - unreachable/connection refused
# LAN 192.168.1.176: 32177 - product/instance/user (listings, searches, connections)
# ..
def ServiceDirectory_NORMAL_NetworkEnquiry(self, message):
	# Here/this level of directory info.
	h = message.lineage[-1]

	listing = [DirectoryRoute(k, v[0].agent_address, v[1]) for k, v in self.directory.items()]
	find = [DirectoryRoute(v[0].requested_search, v[0].agent_address, v[1]) for k, v in self.find.items()]
	accepted = [v.accepted_ipp for v in self.accepted.values()]

	h.scope = self.scope
	h.started = self.started
	h.listing = listing
	h.find = find
	h.accepted = accepted

	if self.scope != ScopeOfService.WAN:
		# Above/next level of directory info.
		not_connected = str(self.not_connected) if self.not_connected else None
		a = DirectoryScope(scope=None, connect_above=self.connect_above, not_connected=not_connected)
		message.lineage.append(a)
		if self.connected_up:
			a.connected = self.connected
			self.forward(message, self.connected_up, self.return_address)
			return NORMAL

	self.reply(DirectoryAncestry(lineage=message.lineage))
	return NORMAL

def ServiceDirectory_NORMAL_NetworkConnect(self, message):
	if message.scope < self.scope:
		a = ScopeOfService.to_name(message.scope)
		b = ScopeOfService.to_name(self.scope)
		f = ar.Faulted(f'cannot reach directory at "{a}"', 'skipped a level?')
		self.reply(f)
		return NORMAL
	elif message.scope > self.scope:
		if not self.connected_up:
			a = ScopeOfService.to_name(message.scope)
			f = ar.Faulted(f'cannot reach directory at "{a}"', 'unable to connect? missing a level?')
			self.reply(f)
			return NORMAL
		self.forward(message, self.connected_up, self.return_address)
		return NORMAL

	self.reconnecting = [message, self.return_address]
	self.send(ar.Anything(message.connect_above), self.parent_address)
	return NORMAL

def ServiceDirectory_NORMAL_Ack(self, message):
	m, a = self.reconnecting[0], self.reconnecting[1]
	self.connect_above = m.connect_above
	self.send(ar.Anything(m.connect_above), self.ctd)
	self.send(ar.Ack(), a)
	return NORMAL

def ServiceDirectory_NORMAL_Completed(self, message):
	key = self.debrief()
	a = self.matched.pop(key, None)
	if a is None:
		return NORMAL

	# Clear key from pub/sub.
	for d in self.directory.values():
		if key in d[1]:
			d[1].discard(key)
			break

	for f in self.find.values():
		if key in f[1]:
			f[1].discard(key)
			break

	return NORMAL

def ServiceDirectory_NORMAL_Stop(self, message):
	self.stopped = self.return_address
	self.abort()
	if self.working():
		return CLEARING
	self.send(ar.Ack(), self.stopped)
	self.complete(ar.Aborted())

def ServiceDirectory_CLEARING_Completed(self, message):
	self.debrief()
	if self.working():
		return CLEARING
	self.send(ar.Ack(), self.stopped)
	self.complete(ar.Aborted())

SERVICE_DIRECTORY_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	OPENING: (
		(Listening, NotListening,
		Accepted, Abandoned,
		ar.Stop,),
		(UseAddress, NoAddress)
	),
	NORMAL: (
		(UseAddress, NoAddress,
		Listening, NotListening,
		Accepted, Closed, Abandoned, ar.T2,
		NotConnected,
		PushedDirectory,
		ServiceListing, FindService,
		UnlistService, UnlistFind,
		CapRoutes, TrimRoutes,
		NetworkEnquiry, NetworkConnect,
		ar.Ack,
		ar.Completed,
		ar.Stop), ()
	),
	CLEARING: (
		(ar.Completed), ()
	),
}

ar.bind(ServiceDirectory, SERVICE_DIRECTORY_DISPATCH)

# The preliminary exchange to trade end-point addresses
#
class OpenLoop(object):
	def __init__(self, subscriber_session=None, key=None):
		self.subscriber_session = subscriber_session
		self.key = key

class LoopOpened(object):
	def __init__(self, publisher_session=None, key=None):
		self.publisher_session = publisher_session
		self.key = key

class CloseLoop(object):
	def __init__(self, key=None):
		self.key = key

INTRODUCTION_SCHEMA = {
	'subscriber_session': ar.Address(),
	'publisher_session': ar.Address(),
	'key': str,
}

ar.bind(OpenLoop, object_schema=INTRODUCTION_SCHEMA)
ar.bind(LoopOpened, object_schema=INTRODUCTION_SCHEMA)
ar.bind(CloseLoop, object_schema=INTRODUCTION_SCHEMA)

#
#
class PublisherLoop(ar.Point, ar.StateMachine):
	def __init__(self, route, remote_session, remote_loop, publisher_address, create_session, relay_address):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.route = route
		self.key = route.key
		self.remote_session = remote_session
		self.remote_loop = remote_loop
		self.publisher_address = publisher_address
		self.create_session = create_session
		self.relay_address = relay_address

		self.session_address = None
		self.origin_address = None
		self.created_session = None
		self.closing = False
		self.value = None

	def close_route(self):
		# Just received or sent CloseLoop.
		if isinstance(self.route, InboundByRelay):
			self.send(CloseRelay(self.route.redirect), self.relay_address)

def PublisherLoop_INITIAL_Start(self, message):
	### PS-pub-7 Loop arranges session.
	cs = self.create_session
	if cs:
		# Create the ending function that swaps the Completed message to the parent for a
		# Clear message to the proxy.
		self.created_session = self.create(cs.object_type, *cs.args,
			controller_address=self.publisher_address, remote_address=self.remote_session,
			**cs.kw)
		self.session_address = self.created_session
		self.origin_address = self.created_session
	else:
		self.session_address = self.publisher_address
		self.origin_address = self.remote_session

	self.send(LoopOpened(self.session_address, self.key), self.remote_loop)
	self.forward(Delivered(self.key, self.address), self.publisher_address, self.origin_address)
	return LOOPED

# Methods of termination;
### PS-pub-8 Loop terminates by session completion.
def PublisherLoop_LOOPED_Completed(self, message):
	if self.created_session and self.return_address == self.created_session:
		self.forward(Cleared(message.value), self.publisher_address, self.origin_address)
		self.send(CloseLoop(self.key), self.remote_loop)
		self.close_route()
		self.complete(ar.Aborted())
	self.warning('Unexpected termination')
	return LOOPED

### PS-pub-8 Loop terminates by local clear().
def PublisherLoop_LOOPED_Close(self, message):
	self.closing, self.value = True, message.value
	self.send(CloseLoop(self.key), self.remote_loop)
	if self.created_session:
		self.send(ar.Stop(), self.created_session)
		return CLEARING
	self.close_route()

	self.forward(Cleared(message.value), self.publisher_address, self.origin_address)
	self.complete(ar.Aborted())

### PS-pub-8 Loop terminates by remote close.
def PublisherLoop_LOOPED_CloseLoop(self, message):
	if self.created_session:
		self.send(ar.Stop(), self.created_session)
		return CLEARING
	self.close_route()

	self.forward(Dropped(), self.publisher_address, self.origin_address)
	self.complete(ar.Aborted())

### PS-pub-8 Loop terminates by local exit.
def PublisherLoop_LOOPED_Stop(self, message):
	self.send(CloseLoop(self.key), self.remote_loop)
	if self.created_session:
		self.send(message, self.created_session)
		return CLEARING
	self.close_route()

	self.forward(Dropped(), self.publisher_address, self.origin_address)
	self.complete(ar.Aborted())

def PublisherLoop_CLEARING_Completed(self, message):
	if self.created_session is None or self.return_address != self.created_session:
		return CLEARING

	self.create_session = None
	self.close_route()

	if self.closing:
		self.forward(Cleared(self.value), self.publisher_address, self.origin_address)
	else:
		self.forward(Dropped(), self.publisher_address, self.origin_address)

	self.complete(ar.Aborted())

PUBLISHER_LOOP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	LOOPED: (
		(ar.Completed, Close, CloseLoop, ar.Stop,), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

ar.bind(PublisherLoop, PUBLISHER_LOOP_DISPATCH, thread='published')

# An object to maintain a listen on behalf of a published
# name. Enters name and listen into the service directory.
class PublishingAgent(ar.Point, ar.StateMachine):
	def __init__(self, requested_name, publisher_address, create_session, declared_scope):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.requested_name = requested_name
		self.publisher_address = publisher_address
		self.create_session = create_session
		self.declared_scope = declared_scope
		self.listening = None
		self.matching = {}
		self.loop = {}
		self.relay = {}
		self.peered = {}
		self.relay_address = {}

def PublishingAgent_INITIAL_Start(self, message):
	if self.declared_scope == ScopeOfService.PROCESS:
		### PS-pub-3 Agent sends listing to directory.
		listing_id = uuid.uuid4()
		self.send(ServiceListing(requested_name=self.requested_name,
			agent_address=self.address, declared_scope=self.declared_scope,
			listing_id=listing_id), pb.directory)
		self.send(Published(self.requested_name, self.declared_scope), self.publisher_address)
		return READY
	elif self.declared_scope in (ScopeOfService.GROUP, ScopeOfService.HOST):
		### PS-pub-3 Agent arranges for inbound listen.
		pb.channel.send(ListenForStream(LocalPort(0)), self.address)
		return PENDING
	elif self.declared_scope in (ScopeOfService.LAN, ScopeOfService.WAN):
		pb.channel.send(ListenForStream(HostPort('0.0.0.0', 0)), self.address)
		return PENDING
	return READY

def PublishingAgent_PENDING_Listening(self, message):
	self.listening = message
	listing_id = uuid.uuid4()
	self.send(ServiceListing(requested_name=self.requested_name,
		agent_address=self.address, declared_scope=self.declared_scope,
		listing_id=listing_id,
		listening_ipp=message.listening_ipp), pb.directory)
	self.send(Published(self.requested_name, self.declared_scope, message.listening_ipp), self.publisher_address)
	return READY

def PublishingAgent_PENDING_NotListening(self, message):
	ipp = message.requested_ipp
	t = message.error_text
	self.warning(f'Cannot allocate a listen for {ipp} ({t})')
	self.start(ar.T1, 60.0)
	return GLARING

def PublishingAgent_PENDING_Stop(self, message):
	self.send(UnlistService(self.requested_name, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

def PublishingAgent_GLARING_T1(self, message):
	if self.declared_scope in (ScopeOfService.GROUP, ScopeOfService.HOST):
		pb.channel.send(ListenForStream(LocalPort(0)), self.address)
		return PENDING
	elif self.declared_scope in (ScopeOfService.LAN, ScopeOfService.WAN):
		pb.channel.send(ListenForStream(HostPort('0.0.0.0', 0)), self.address)
		return PENDING
	return READY

def PublishingAgent_GLARING_Stop(self, message):
	self.send(UnlistService(self.requested_name, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

def looped(self, inbound, open, return_address):
	if inbound is None or open is None or return_address is None:
		return
	key = open.key
	relay_address = self.relay_address.get(key, None)
	### PS-pub-6 Agent creates local loop.
	a = self.create(PublisherLoop, inbound, open.subscriber_session, return_address,
		self.publisher_address, self.create_session,
		relay_address)
	self.assign(a, key)
	self.loop[key] = a

### PS-pub-4 Agent accepts internal route.
def PublishingAgent_READY_InboundFromAddress(self, message):
	key = message.key

	try:
		m = self.matching[key]
	except KeyError:
		m = [message, None, None]
		self.matching[key] = m
		self.trace(f'Added direct route [{ScopeOfService.to_name(message.scope)}]({key})')
		return READY
	looped(self, message, m[1], m[2])
	return READY

### PS-pub-4 Agent accepts peer route.

def PublishingAgent_READY_InboundOverAccepted(self, message):
	key = message.key

	try:
		m = self.matching[key]
	except KeyError:
		m = [message, None, None]
		self.matching[key] = m
		self.trace(f'Added peer route [{ScopeOfService.to_name(message.scope)}]({key})')
		return READY
	looped(self, message, m[1], m[2])
	return READY

def PublishingAgent_READY_InboundByRelay(self, message):
	key = message.key
	try:
		relay = self.relay[key]
		self.warning(f'Duplicate relay "{key}" (ignored)')
		return READY
	except KeyError:
		relay = message
		self.relay[key] = relay

	ipp = relay.redirect.redirect_ipp
	k = ipp_key(ipp)

	try:
		r = self.peered[k]
		r[1][key] = relay
		n = len(r[1])
		self.trace(f'Peer for relay "{key}" already known ({n} routes pending)')
	except KeyError:
		r = [None, {key: relay}]
		self.peered[k] = r

		self.trace(f'Opening peer "{k}" (relay {key})')
		self.send(OpenPeer(ipp, key), pb.house)
		return READY

	if r[0] is None:
		return READY

	self.send(relay, r[0])
	self.relay_address[key] = r[0]
	# Assume the same state as for other route types, i.e.
	# ready for the OpenLoop that is sure to follow.
	try:
		m = self.matching[key]
	except KeyError:
		m = [relay, None, None]
		self.matching[key] = m
		self.trace(f'Added relay peer [{ScopeOfService.to_name(relay.scope)}]({key})')
		return READY
	looped(self, message, m[1], m[2])
	return READY
	
def PublishingAgent_READY_PeerOpened(self, message):
	k = ipp_key(message.connecting_ipp)
	try:
		r = self.peered[k]
	except KeyError:
		self.warning(f'Unknown peer opened"{k}"')
		return READY
	r[0] = self.return_address

	for key, relay in r[1].items():
		self.reply(relay)
		self.relay_address[key] = self.return_address
		# Assume the same state as for other route types, i.e.
		# ready for the OpenLoop that is sure to follow.
		try:
			m = self.matching[key]
		except KeyError:
			m = [relay, None, None]
			self.matching[key] = m
			self.trace(f'Added relay peer [{ScopeOfService.to_name(relay.scope)}]({key})')
			continue
		looped(self, message, m[1], m[2])
	return READY

def PublishingAgent_READY_RetractRoute(self, message):
	key = message.key

	m = self.matching.pop(key, None)
	if m is None:
		self.trace(f'Unknown key "{key}"')
		return READY

	if m[0] is None:
		self.trace(f'Known key "{key}" never routed')
		return READY

	self.trace(f'Retracted route [{ScopeOfService.to_name(m[0].scope)}]({key})')
	return READY

### PS-pub-5 Agent accepts remote loop.
def PublishingAgent_READY_OpenLoop(self, message):
	key = message.key
	try:
		m = self.matching[key]
	except KeyError:
		m = [None, message, self.return_address]
		self.matching[key] = m
		return READY
	looped(self, m[0], message, self.return_address)
	return READY

def PublishingAgent_READY_CloseLoop(self, message):
	key = message.key
	loop = self.loop.get(key, None)
	if loop:
		self.forward(message, loop, self.return_address)
	return READY

def PublishingAgent_READY_CapRoutes(self, message):
	self.trace(f'Scope cap {message.service_scope}, {len(self.matching)} routes to consider')

	removing = set()
	for k, m in self.matching.items():
		if message.service_scope < m[0].scope:
			removing.add(k)

	self.trace(f'Removing {len(removing)} routes')
	for k in removing:
		m = self.matching.pop(k, None)
		if m is None:
			continue
		m0 = m[0]
		if m0 is None:
			continue
		self.trace(f'Capped route [{ScopeOfService.to_name(m0.scope)}]({k})')
	return READY

def PublishingAgent_READY_Clear(self, message):
	if message.session is None:
		for a in self.loop.values():
			self.send(Close(message.value), a)
		return READY

	key = message.session.key
	try:
		a = self.loop[key]
	except KeyError:
		return READY
	self.send(Close(message.value), a)

	return READY

def PublishingAgent_READY_NotPeered(self, message):
	if message.session is None:
		for a in self.loop.values():
			# Was CloseLoop().
			self.send(ar.Stop(), a)
		return READY

	key = message.key
	try:
		a = self.loop[key]
	except KeyError:
		return READY
	# Was CloseLoop().
	self.send(ar.Stop(), a)

	return READY

def PublishingAgent_READY_Completed(self, message):
	key = self.debrief()
	self.loop.pop(key, None)
	return READY

def PublishingAgent_READY_Ping(self, message):
	self.reply(ar.Ack())
	return READY

def PublishingAgent_READY_Stop(self, message):
	if self.working():
		self.abort()
		return CLEARING
	self.send(UnlistService(self.requested_name, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

def PublishingAgent_CLEARING_Completed(self, message):
	key = self.debrief()
	self.loop.pop(key, None)
	if self.working():
		return CLEARING
	self.send(UnlistService(self.requested_name, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

PUBLISHING_AGENT_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Listening, NotListening, ar.Stop), ()
	),
	GLARING: (
		(ar.T1, ar.Stop), ()
	),
	READY: (
		(InboundFromAddress, InboundOverAccepted, InboundByRelay, PeerOpened,
		RetractRoute, CapRoutes,
		OpenLoop, CloseLoop, Clear, NotPeered,
		ar.Ping,
		ar.Completed, ar.Stop), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

ar.bind(PublishingAgent, PUBLISHING_AGENT_DISPATCH, thread='published')

#
#
class ReRoute(object):
	def __init__(self, route=None):
		self.route = route

SHORTER_ROUTE_SCHEMA = {
	'route': ar.Any(),
}

ar.bind(ReRoute, object_schema=SHORTER_ROUTE_SCHEMA)

# States of the machine.
#

SECONDS_OF_LOOPING = 4.0
SECONDS_OF_PEERING = 4.0

# Pick out the best route in the
# given table.
def best_route(table):
	scope, route = None, None
	for s, r in table.items():
		if scope is None or s < scope:
			scope, route = s, r
	return scope, route

def find_route(table, key):
	for s, r in table.items():
		if r.key == key:
			return s
	return None

class SubscriberLoop(ar.Point, ar.StateMachine):
	def __init__(self, route, subscriber_address, create_session):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.route = route
		self.subscriber_address = subscriber_address
		self.create_session = create_session

		# Context of a routing attempt
		self.remote_agent = None
		self.peer_ipp = None
		self.peer_address = None
		self.clearing_value = None

		# Context of a looped route
		self.latch = None
		self.remote_session = None
		self.session_address = None
		self.origin_address = None

	def open_loop(self, key, remote_agent):
		self.remote_agent = remote_agent
		# WARNING - ADDRESS OF LATCH CHANGES
		self.trace(f'Initiate latch/loop to "{key}"')
		a = self.create(ar.Latch, key, self.subscriber_address)
		self.assign(a, 0)
		self.latch = a
		self.send(OpenLoop(a, key), remote_agent)
		self.start(ar.T1, SECONDS_OF_LOOPING)

	def open_peer(self):
		key = self.route.key
		ipp = self.route.connecting_ipp
		self.peer_ipp = ipp
		self.trace(f'Requests peer {ipp} for "{key}"')
		self.send(OpenPeer(ipp, key), pb.house)
		self.start(ar.T2, SECONDS_OF_PEERING)

	def open_relay(self):
		key = self.route.key
		ipp = self.route.redirect.redirect_ipp
		self.peer_ipp = ipp
		self.trace(f'Requests relay {ipp} for "{key}"')
		self.send(OpenPeer(ipp, key), pb.house)
		self.start(ar.T2, SECONDS_OF_PEERING)

	def open_latch(self, message):
		self.remote_loop = self.return_address
		self.remote_session = message.publisher_session
		if self.create_session:
			cs = self.create_session
			session = self.create(cs.object_type, *cs.args,
				controller_address=self.subscriber_address, remote_address=self.remote_session,
				**cs.kw)
			self.assign(session, 1)			# 0 (zero) is the latch
			self.session_address = session
			self.origin_address = session
			# ABDICATE slot to session
			# self.alias = self.abdicate_to(session)
			# Latch clears additional session alias on stop
			hand = ar.SwitchOver(session)
		else:
			self.session_address = self.subscriber_address
			self.origin_address = self.remote_session
			# ABDICATE slot to controller
			# Latch clears additional session alias on stop
			hand = ar.SwitchOver()
		# Sending session control message from Latch is flawed - doesnt know
		# about "origin_address".
		s = address_to_text(self.subscriber_address)
		p = address_to_text(self.origin_address)
		self.trace(f'Loop opened between subscriber [{s}] and publisher [{p}]')
		self.forward(Available(message.key, self.parent_address), self.subscriber_address, self.origin_address)
		self.send(hand, self.latch)
		# LATCH MUST CONTINUE FOR THOSE MESSAGES THAT WERE
		# SITTING IN THE QUEUE AFTER THE HANDOVER MESSAGE
	
	def latch_loop(self):
		j = self.address_job.pop(self.latch, None)
		if j is None:
			self.warning(f'Where is the latch entry?')
		self.assign(self.return_address, 0)

	def close_loop(self):
		key = self.route.key
		self.trace(f'Close loop for "{key}"')
		self.send(CloseLoop(key), self.remote_agent)

	def close_peer(self):
		key = self.route.key
		ipp = self.peer_ipp
		self.trace(f'Close peer {ipp} for "{key}"')
		self.send(ClosePeer(ipp, key), pb.house)

	def close_relay(self):
		self.send(CloseRelay(self.route.redirect), self.peer_address)

#
#
def SubscriberLoop_INITIAL_Start(self, message):
	route = self.route
	e = ScopeOfService.to_name(route.scope)
	self.trace(f'Initiate route [{e}]({route.key})')

	if isinstance(route, RouteToAddress):
		self.open_loop(route.key, route.address)
		return LOOPING
	elif isinstance(route, RouteOverConnected):
		self.open_peer()
		return CONNECTION_PEERING
	elif isinstance(route, RouteByRelay):
		self.open_relay()
		return RELAY_PEERING

	unknown = ar.Faulted(f'Cannot initiate route ({route.key})', f'unknown scope [{e}]')
	self.warning(f'{unknown}')
	self.complete(unknown)

# LOOPING.
def SubscriberLoop_LOOPING_LoopOpened(self, message):
	self.open_latch(message)
	return LATCHING

def SubscriberLoop_LOOPING_T1(self, message):
	self.close_loop()
	self.complete(ar.TimedOut(message))

def SubscriberLoop_LOOPING_Stop(self, message):
	self.close_loop()
	self.complete(ar.Aborted())

# LATCHING
def SubscriberLoop_LATCHING_Ack(self, message):
	self.latch_loop()
	return LOOPED

# LOOPED
# Completed -> session object terminated
# Close -> controller
# CloseLoop -> remote termination
# PeerLost -> network abandoned
# Stop -> application
def SubscriberLoop_LOOPED_Completed(self, message):
	d = self.debrief()
	# 0) Latch, 1) Session, *) Unknown
	if d == 1:
		self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)
	else:
		f = ar.Faulted('Loop management', f'unexpected completion {d}')
		self.warning(str(f))
		self.forward(Cleared(f), self.subscriber_address, self.origin_address)

	self.close_loop()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

# Local termination.
def SubscriberLoop_LOOPED_Close(self, message):
	self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)

	self.close_loop()
	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

# Remote termination.
def SubscriberLoop_LOOPED_CloseLoop(self, message):
	self.forward(Dropped('Closed by remote'), self.subscriber_address, self.origin_address)

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_LOOPED_Stop(self, message):
	self.forward(Cleared(ar.Aborted()), self.subscriber_address, self.origin_address)

	self.close_loop()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

# CONNECTION
def SubscriberLoop_CONNECTION_PEERING_PeerOpened(self, message):
	self.peer_address = self.return_address
	self.open_loop(message.key, self.return_address)
	return CONNECTION_LOOPING

def SubscriberLoop_CONNECTION_PEERING_NotPeered(self, message):
	name = key_service(message.key)
	self.trace(f'Cannot loop to {name} ({message.reason})')
	self.forward(NotAvailable(message.key, message.reason, self.parent_address), self.subscriber_address, self.address)

	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_PEERING_T2(self, message):
	key = self.opened_route.key
	name = key_service(key)
	reason = 'timed out on peer'
	self.trace(f'Cannot loop to {name} ({reason})')
	self.forward(NotAvailable(key, reason, self.parent_address), self.subscriber_address, self.address)

	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_PEERING_Stop(self, message):
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_LOOPING_LoopOpened(self, message):
	self.open_latch(message)
	return CONNECTION_LATCHING

def SubscriberLoop_CONNECTION_LOOPING_T1(self, message):
	key = self.opened_route.key
	name = key_service(key)
	reason = 'timed out on loop'
	self.trace(f'Cannot loop to {name} ({reason})')
	self.forward(NotAvailable(key, reason, self.parent_address), self.subscriber_address, self.address)

	self.close_loop()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_LOOPING_Stop(self, message):
	self.close_loop()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_LATCHING_Ack(self, message):
	self.latch_loop()
	return CONNECTION_LOOPED

def SubscriberLoop_CONNECTION_LOOPED_Completed(self, message):
	d = self.debrief()
	# 0) Latch, 1) Session, *) Unknown
	if d == 1:
		self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)
	else:
		f = ar.Faulted('Loop management', f'unexpected completion {d}')
		self.warning(str(f))
		self.forward(Cleared(f), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_peer()
	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

def SubscriberLoop_CONNECTION_LOOPED_Close(self, message):
	self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

def SubscriberLoop_CONNECTION_LOOPED_CloseLoop(self, message):
	self.forward(Dropped('Closed by remote'), self.subscriber_address, self.origin_address)

	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_LOOPED_PeerLost(self, message):
	self.forward(Dropped('Abandoned by peer'), self.subscriber_address, self.origin_address)

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CONNECTION_LOOPED_Stop(self, message):
	self.forward(Cleared(ar.Aborted()), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

# RELAY
def SubscriberLoop_RELAY_PEERING_PeerOpened(self, message):
	self.peer_address = self.return_address
	self.reply(self.route)
	self.open_loop(message.key, self.return_address)
	return RELAY_LOOPING

def SubscriberLoop_RELAY_PEERING_NotPeered(self, message):
	name = key_service(message.key)
	self.trace(f'Cannot relay to {name} ({message.reason})')
	self.forward(NotAvailable(message.key, message.reason, self.parent_address), self.subscriber_address, self.address)

	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_RELAY_PEERING_T2(self, message):
	key = self.opened_route.key
	name = key_service(key)
	reason = 'timed out on peer'
	self.trace(f'Cannot relay to {name} ({reason})')
	self.forward(NotAvailable(key, reason, self.parent_address), self.subscriber_address, self.address)

	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_RELAY_PEERING_Stop(self, message):
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

def SubscriberLoop_RELAY_LOOPING_LoopOpened(self, message):
	self.open_latch(message)
	return RELAY_LATCHING

def SubscriberLoop_RELAY_LOOPING_T1(self, message):
	key = self.opened_route.key
	name = key_service(key)
	reason = 'timed out on loop'
	self.trace(f'Cannot relay to {name} ({reason})')
	self.forward(NotAvailable(key, reason, self.parent_address), self.subscriber_address, self.address)

	self.close_loop()
	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

def SubscriberLoop_RELAY_LOOPING_Stop(self, message):
	self.close_loop()
	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

def SubscriberLoop_RELAY_LATCHING_Ack(self, message):
	self.latch_loop()
	return RELAY_LOOPED

def SubscriberLoop_RELAY_LOOPED_Completed(self, message):
	d = self.debrief()
	# 0) Latch, 1) Session, *) Unknown
	if d == 1:
		self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)
	else:
		f = ar.Faulted('Loop management', f'unexpected completion {d}')
		self.warning(str(f))
		self.forward(Cleared(f), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

# Local termination.
def SubscriberLoop_RELAY_LOOPED_Close(self, message):
	self.forward(Cleared(message.value), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = True
		return CLEARING
	self.complete(True)

# Remote termination.
def SubscriberLoop_RELAY_LOOPED_CloseLoop(self, message):
	self.forward(Dropped('Closed by remote'), self.subscriber_address, self.origin_address)

	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

# Termination by loss of peer.
def SubscriberLoop_RELAY_LOOPED_PeerLost(self, message):
	self.forward(Dropped('Abandoned by peer'), self.subscriber_address, self.origin_address)

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_RELAY_LOOPED_Stop(self, message):
	self.forward(Cleared(ar.Aborted()), self.subscriber_address, self.origin_address)

	self.close_loop()
	self.close_relay()
	self.close_peer()

	if self.working():
		self.abort()
		self.clearing_value = False
		return CLEARING
	self.complete(False)

def SubscriberLoop_CLEARING_Completed(self, message):
	self.debrief()
	if self.working():
		return CLEARING
	self.complete(self.clearing_value)

SUBSCRIBER_LOOP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	LOOPING: (
		(LoopOpened, ar.T1, ar.Stop), (Close,)
	),
	LATCHING: (
		(ar.Ack,), (CloseLoop, ar.Completed, Close, ar.Stop)
	),
	LOOPED: (
		(ar.Completed, Close, CloseLoop, ar.Stop), ()
	),
	CONNECTION_PEERING: (
		(PeerOpened, NotPeered, ar.T2, ar.Stop), (Close,)
	),
	CONNECTION_LOOPING: (
		(LoopOpened, ar.T1, ar.Stop), (PeerLost, Close)
	),
	CONNECTION_LATCHING: (
		(ar.Ack,), (CloseLoop, ar.Completed, PeerLost, Close, ar.Stop)
	),
	CONNECTION_LOOPED: (
		(ar.Completed, Close, CloseLoop, PeerLost, ar.Stop), ()
	),
	RELAY_PEERING: (
		(PeerOpened, NotPeered, ar.T2, ar.Stop), (Close,)
	),
	RELAY_LOOPING: (
		(LoopOpened, ar.T1, ar.Stop), (PeerLost, Close)
	),
	RELAY_LATCHING: (
		(ar.Ack,), (CloseLoop, ar.Completed, PeerLost, Close, ar.Stop)
	),
	RELAY_LOOPED: (
		(ar.Completed, Close, CloseLoop, PeerLost, ar.Stop), ()
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

# WARNING agent and loop MUST be on same thread.
ar.bind(SubscriberLoop, SUBSCRIBER_LOOP_DISPATCH, thread='subscribed')

# An object that represents a unique instance of a subscriber object
# and a requested search, i.e. each subscriber can have multiple
# active searches (as long as they are different) and each search can
# match multiple publishers.
class SubscriptionAgent(ar.Point, ar.StateMachine):
	def __init__(self, requested_search, subscriber_address, create_session, declared_scope):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.requested_search = requested_search
		self.subscriber_address = subscriber_address
		self.create_session = create_session
		self.declared_scope = declared_scope
		self.service_looping = {}

	def open_route(self, route, tag):
		name = key_service(route.key)
		scope = route.scope
		sos = ScopeOfService.to_name(scope)

		looping = self.service_looping.get(name, None)
		if looping is None:
			self.trace(f'Start loop "{name}" [{sos}] {tag}')
			table = {scope: route}
			a = self.create(SubscriberLoop, route, self.subscriber_address, self.create_session)
			self.assign(a, name)
			looping = [table, route, a, False]		# Table, route, loop, completion.
			self.service_looping[name] = looping
			return

		table, opened, loop, completed = looping
		table[scope] = route

		if route.scope == opened.scope:
			if loop:
				self.trace(f'Replacement [{sos}] route (loop running)')
				return
			if completed:
				self.trace(f'Replacement [{sos}] route (previous positive completion)')
				return

			route_id = key_id(route.key)
			opened_id = key_id(opened.key)
			if route_id == opened_id:
				self.trace(f'Replacement [{sos}] route (no change)')
				return

			if id_process(route_id) != id_process(opened_id):
				s = 'process'
			elif id_connection(route_id) != id_connection(opened_id):
				s = 'connection'
			else:
				self.warning(f'Replacement [{sos}] route (change of id but not process or connection)')
				return

			self.trace(f'Start replacement [{sos}] route for "{name}", change of {s}')
			a = self.create(SubscriberLoop, route, self.subscriber_address, self.create_session)
			self.assign(a, name)
			looping[1] = route
			looping[2] = a
			return

		if route.scope < opened.scope:
			if loop:
				self.trace(f'Upgrade [{sos}] route, pushing current loop')
				self.send(ar.Stop(), loop)
				return
			if completed:
				self.trace(f'Upgrade [{sos}] route, (previous positive completion)')
				return

			self.trace(f'Start upgrade [{sos}] route for "{name}"')
			a = self.create(SubscriberLoop, route, self.subscriber_address, self.create_session)
			self.assign(a, name)
			looping[1] = route
			looping[2] = a
			return

		self.trace(f'Fallback [{sos}] route')


# Register interest in services matching pattern.
def SubscriptionAgent_INITIAL_Start(self, message):
	self.send(FindService(self.requested_search, self.address, self.declared_scope), pb.directory)
	return READY

# Routes arrive from directories. This is the first moment of discovering
# new matching service names. Instantiate per-match object as needed,
# that will initiate and manage actual session with remote.
def SubscriptionAgent_READY_RouteToAddress(self, message):
	self.open_route(message, f'{message.address}')
	return READY

def SubscriptionAgent_READY_RouteOverConnected(self, message):
	tag = f'{message.connecting_ipp}'
	self.open_route(message, tag)
	return READY

def SubscriptionAgent_READY_RouteByRelay(self, message):
	tag = f'{message.redirect.redirect_ipp}'
	self.open_route(message, tag)
	return READY

def SubscriptionAgent_READY_RetractRoute(self, message):
	key = message.key
	name = key_service(key)

	looping = self.service_looping.get(name, None)
	if looping is None:
		self.trace(f'Retract for unknown service "{name}"')
		return READY
	table = looping[0]

	scope = find_route(table, key)
	if scope is None:
		self.trace(f'Retract for unknown route "{key}"')
		return READY

	r = table.pop(scope, None)
	if r is None:
		self.warning(f'Find/pop failed for route "{key}"')
		return READY

	return READY

def SubscriptionAgent_READY_CapRoutes(self, message):
	for name, looping in self.service_looping.items():
		table = looping[0]
		for s in range(message.service_scope + 1, ScopeOfService.WAN + 1):
			table.pop(s, None)
	return READY

def SubscriptionAgent_READY_Clear(self, message):
	if message.session is None:
		self.warning('No session included')
		return READY

	key = message.session.key
	name = key_service(key)

	looping = self.service_looping.get(name, None)
	if looping is None:
		self.warning(f'Clear of unknown service {name}')
		return READY

	self.send(Close(message.value), looping[2])
	return READY

def SubscriptionAgent_READY_Ping(self, message):
	self.reply(ar.Ack())
	return READY

def SubscriptionAgent_READY_Completed(self, message):
	name = self.debrief()

	# Discard (pop) the object entry and recover (get) the
	# routing table for the named service.
	looping = self.service_looping.get(name, None)
	if looping is None:
		self.warning(f'Completion of unknown loop {name}')
		return READY
	looping[2] = None
	looping[3] = message.value

	table, route, loop, completed = looping

	if completed:			# This subscriber/publisher match is done.
		return READY

	scope, best = best_route(table)		# Nothing to route to.
	if scope is None:
		return READY

	sos = ScopeOfService.to_name(route.scope)
	if best.scope == route.scope:
		self.trace(f'Replacement [{sos}] route')
		if key_id(best.key) == key_id(route.key):
			self.trace(f'Replacement route for "{name}" has not changed')
			return READY

	self.trace(f'Start continuation loop "{name}" [{sos}]')
	a = self.create(SubscriberLoop, message, self.subscriber_address, self.create_session)
	self.assign(a, name)
	looping[1] = message
	looping[2] = a
	return READY

def SubscriptionAgent_READY_Stop(self, message):
	if self.working():
		self.abort()
		return COMPLETING
	self.send(UnlistFind(self.requested_search, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

def SubscriptionAgent_COMPLETING_Completed(self, message):
	name = self.debrief()
	looping = self.service_looping.get(name, None)
	if looping is None:
		self.warning(f'Untidy completion of {name}')

	if self.working():
		return COMPLETING
	self.send(UnlistFind(self.requested_search, self.address, self.declared_scope), pb.directory)
	self.complete(ar.Aborted())

SUBSCRIPTION_AGENT_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	READY: (
		(RouteToAddress, RouteOverConnected, RouteByRelay, RetractRoute, CapRoutes,
		Clear,
		ar.Ping,
		ar.Completed, ar.Stop), ()
	),
	COMPLETING: (
		(ar.Completed,), ()
	),
}

# WARNING agent and loop MUST be on same thread.
ar.bind(SubscriptionAgent, SUBSCRIPTION_AGENT_DISPATCH, thread='subscribed')

#
#
class ConnectToPeer(ar.Point, ar.StateMachine):
	def __init__(self, connecting_ipp, key, client_address):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.connecting_ipp = connecting_ipp
		self.key = key
		self.connected = None
		self.not_connected = None
		self.client_address = set()
		self.client_address.add(client_address)

def ConnectToPeer_INITIAL_Start(self, message):
	connect(self, self.connecting_ipp)
	return CONNECTING

# CONNECTING
#
def ConnectToPeer_CONNECTING_Connected(self, message):
	self.connected = message

	return_address = self.return_address
	opened = PeerOpened(connecting_ipp=self.connecting_ipp, key=self.key)
	for c in self.client_address:
		self.forward(opened, c, return_address)

	return CONNECTED

def ConnectToPeer_CONNECTING_NotConnected(self, message):
	self.not_connected = str(message)
	not_peered = NotPeered(connecting_ipp=self.connecting_ipp, key=self.key, reason=self.not_connected)
	for c in self.client_address:
		self.send(not_peered, c)

	self.start(ar.T1, 4.0)
	return GLARING

def ConnectToPeer_CONNECTING_Stop(self, message):
	self.complete(ar.Aborted())

# CONNECTED
#
def ConnectToPeer_CONNECTED_Abandoned(self, message):
	self.not_connected = 'Abandoned by remote'
	return_address = self.return_address
	lost = PeerLost(connecting_ipp=self.connecting_ipp, key=self.key)
	for c in self.client_address:
		self.forward(lost, c, return_address)
	self.start(ar.T1, 4.0)
	return GLARING

def ConnectToPeer_CONNECTED_Closed(self, message):
	self.not_connected = 'Local termination'
	return_address = self.return_address
	lost = PeerLost(connecting_ipp=self.connecting_ipp, key=self.key)
	for c in self.client_address:
		self.forward(lost, c, return_address)
	self.start(ar.T1, 4.0)
	return GLARING

def ConnectToPeer_CONNECTED_OpenPeer(self, message):
	self.client_address.add(self.return_address)
	opened = PeerOpened(connecting_ipp=self.connecting_ipp, key=self.key)
	self.forward(opened, self.return_address, self.connected.remote_address)
	return CONNECTED

def ConnectToPeer_CONNECTED_ClosePeer(self, message):
	self.client_address.discard(self.return_address)
	if len(self.client_address) < 1:
		self.not_connected = 'Cleared last peer'
		self.send(Close(ar.Aborted()), self.connected.remote_address)
		self.start(ar.T1, 4.0)
		return GLARING
	return CONNECTED

def ConnectToPeer_CONNECTED_Stop(self, message):
	self.not_connected = 'Process termination'
	return_address = self.connected.remote_address
	lost = PeerLost(connecting_ipp=self.connecting_ipp, key=self.key)
	for c in self.client_address:
		self.forward(lost, c, return_address)
	self.send(Close(ar.Aborted()), return_address)
	return CLOSING

# GLARING
def ConnectToPeer_GLARING_T1(self, message):
	self.complete(ar.Aborted())

def ConnectToPeer_GLARING_OpenPeer(self, message):
	reason = self.not_connected
	np = NotPeered(connecting_ipp=self.connecting_ipp, key=self.key, reason=reason)
	self.reply(np)
	return GLARING

def ConnectToPeer_GLARING_ClosePeer(self, message):
	return GLARING

def ConnectToPeer_GLARING_Closed(self, message):
	return GLARING

def ConnectToPeer_GLARING_Stop(self, message):
	self.complete(ar.Aborted())

# CLOSING
#
def ConnectToPeer_CLOSING_Closed(self, message):
	self.complete(message.value)

def ConnectToPeer_CLOSING_Stop(self, message):
	self.complete(ar.Aborted())

CONNECT_TO_PEER_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	CONNECTING: (
		(Connected, NotConnected, ar.Stop), (OpenPeer, ClosePeer)
	),
	CONNECTED: (
		(Abandoned, Closed, OpenPeer, ClosePeer, ar.Stop), ()
	),
	GLARING: (
		(ar.T1, OpenPeer, ClosePeer, Closed, ar.Stop), ()
	),
	CLOSING: (
		(Closed, ar.Stop), ()
	),
}

ar.bind(ConnectToPeer, CONNECT_TO_PEER_DISPATCH, thread='connect-to-peer')

# Container of publish/subscibe objects. Need something
# to manage their existence and being separate keeps
# directory simpler.
class PubSub(ar.Threaded, ar.StateMachine):
	def __init__(self):
		ar.Threaded.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.published = {}
		self.subscribed = {}
		self.connecting = {}

def PubSub_INITIAL_Start(self, message):
	return NORMAL

### PS-pub-1 Process the app request
def PubSub_NORMAL_PublishAsName(self, message):
	try:
		a = self.published[message.requested_name]
		self.reply(NotPublished(message.requested_name, 'already published'))
		return NORMAL
	except KeyError:
		pass
	### PS-pub-2 Create the agent
	a = self.create(PublishingAgent, message.requested_name, self.return_address, message.create_session, message.declared_scope)
	p = [message, self.return_address]
	self.assign(a, p)
	self.published[message.requested_name] = a
	return NORMAL

### PS-sub-1 Process the app request
def PubSub_NORMAL_SubscribeToName(self, message):
	k = address_to_text(self.return_address)
	k += ':'
	k += message.requested_search
	try:
		a = self.subscribed[k]
	except KeyError:
		### PS-sub-2 Create the agent
		a = self.create(SubscriptionAgent, message.requested_search, self.return_address, message.create_session, message.declared_scope)
		s = [message, self.return_address]
		self.assign(a, s)
		self.subscribed[k] = a
	self.forward(Subscribed(message.requested_search, message.declared_scope), self.return_address, a)
	return NORMAL

def PubSub_NORMAL_Retract(self, message):
	self.trace(f'Retracting service/search at [{address_to_text(message.address)}]')
	for t, a in self.running():
		if t[1] == message.address:
			self.send(ar.Stop(), a)
	return NORMAL

def PubSub_NORMAL_Completed(self, message):
	ma = self.debrief()
	m, a = ma
	if isinstance(m, PublishAsName):
		p = self.published.pop(m.requested_name, None)
		if p is None:
			self.warning(f'Completion of unknown publication key {m.requested_name}')
	elif isinstance(m, SubscribeToName):
		search = m.requested_search
		k = address_to_text(a)
		k += ':'
		k += search
		s = self.subscribed.pop(k, None)
		if s is None:
			self.warning(f'Completion of unknown subscription key {k}')
	elif isinstance(m, HostPort):
		inet = m.inet()
		connecting = self.connecting.pop(inet, None)
		if connecting is None:
			self.trace(f'Completion of unknown peer {inet}')
	else:
		self.warning(f'Completion of unknown type {type(m)}')
	return NORMAL

def PubSub_NORMAL_OpenPeer(self, message):
	inet = message.connecting_ipp.inet()
	connecting = self.connecting.get(inet, None)
	if connecting is None:
		connecting = self.create(ConnectToPeer, message.connecting_ipp, message.key, self.return_address)
		p = [message.connecting_ipp, self.return_address]
		self.assign(connecting, p)
		self.connecting[inet] = connecting
	else:
		self.forward(message, connecting, self.return_address)
	return NORMAL

def PubSub_NORMAL_ClosePeer(self, message):
	inet = message.connecting_ipp.inet()
	connecting = self.connecting.get(inet, None)
	if connecting is None:
		return NORMAL
	self.forward(message, connecting, self.return_address)
	return NORMAL

def PubSub_NORMAL_CapRoutes(self, message):
	self.trace(f'Capping services and searches to [{ScopeOfService.to_name(message.service_scope)}]')
	for m, a in self.running():
		if not isinstance(m, list) or len(m) != 2:
			continue
		if isinstance(m[0], (PublishAsName, SubscribeToName)):
			self.send(message, a)
		elif not isinstance(m[0], HostPort):
			self.trace(f'Cannot cap unknown type {type(m)}')
	return NORMAL

def PubSub_NORMAL_Stop(self, message):
	if self.working():
		self.abort()
		return COMPLETING

	self.complete(ar.Aborted())

def PubSub_COMPLETING_Completed(self, message):
	self.debrief()
	if self.working():
		return COMPLETING

	# This clears the publish/subscribe objects but
	# not the peer connections. Leave that to the
	# framework.
	self.complete(ar.Aborted())

PUBSUB_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	NORMAL: (
		(PublishAsName,	SubscribeToName,
		Retract,
		ar.Completed,
		OpenPeer, ClosePeer,
		CapRoutes,
		ar.Stop), ()
	),
	COMPLETING: (
		(ar.Completed), ()
	),
}

ar.bind(PubSub, PUBSUB_DISPATCH)

# The public interface to the directory service.
#

### PS-pub-0 Start of publish
def publish(self, requested_name, create_session=None, declared_scope=ScopeOfService.WAN):
	self.send(PublishAsName(requested_name, create_session, declared_scope), pb.house)

### PS-sub-0 Start of subscribe
def subscribe(self, requested_search, create_session=None, declared_scope=ScopeOfService.WAN):
	self.send(SubscribeToName(requested_search, create_session, declared_scope), pb.house)

def clear(self, session, value=None):
	self.send(Clear(session, value), session.agent_address)

def retract(self):
	self.send(Retract(self.address), pb.house)
