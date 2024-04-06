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
from .transporting import *
from .plumbing import *
from .directory_if import *
from .directory import *
from .networking_if import *

__all__ = [
	'ConnectToAddress',
	'ListenAtAddress',
	'SubscribeToListing',
	'PublishAListing',
	'SubscribeToSearch',
]

#
#
class INITIAL: pass
class PENDING: pass
class CONNECTED: pass
class GLARING: pass
class CLOSING: pass
class ACCEPTING: pass
class READY: pass

#
#
class ConnectToAddress(ar.Point, ar.StateMachine):
	def __init__(self, ipp, keep_connected=True, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.ipp = ipp
		self.keep_connected = keep_connected
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.connected = None
		self.remote = None

		self.closing = None
		self.intervals = None
		self.retry = None

	def reschedule(self):
		if self.intervals is None:
			s = local_private_public(self.ipp.host)
			r = ip_retry(s)
			self.intervals = r
		
		if self.retry is None:
			self.retry = ar.smart_intervals(self.intervals)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def ConnectToAddress_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()
	connect(self, self.ipp, session=self.session)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of connect.
# Transport established.
def ConnectToAddress_PENDING_Connected(self, message):
	self.connected = message
	self.remote = self.return_address

	# Remote object is ready.
	self.send(UseAddress(self.return_address), self.parent_address)
	return CONNECTED

def ConnectToAddress_PENDING_NotConnected(self, message):
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToAddress_PENDING_Stop(self, message):
	# Local termination.
	# Connected could be orphaned here.
	self.complete(ar.Aborted())

# CONNECTED
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def ConnectToAddress_CONNECTED_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CONNECTED

def ConnectToAddress_CONNECTED_Abandoned(self, message):
	# Normal end of a session.
	# Are there intended to be others?
	if self.keep_connected:
		# Start the retries up again.
		self.started = ar.world_now()
		self.attempts = 0
		self.retry = None
		if self.reschedule():
			# Update the owner that the current session
			# is over.
			self.send(NoAddress(), self.parent_address)
			return GLARING
		# Will only happen on a retry value that
		# allows no retries.
		x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
		self.complete(x)

	# End of session and only wanted 1.
	self.complete(message)

def ConnectToAddress_CONNECTED_Stop(self, message):
	# This object ended by app. Take that as
	# signal to end this session and not activate retries.

	e = ar.Stop() if self.session else Close(ar.Aborted())

	self.send(e, self.remote)
	return CLOSING

def ConnectToAddress_CONNECTED_Closed(self, message):
	# Local end has sent close to the proxy. Treat this
	# as a short-circuit version of above.
	self.complete(message.value)

# GLARING
# After a failed attempt or after abandoned.
def ConnectToAddress_GLARING_Unknown(self, message):
	# Non-control message sneaking through.
	self.forward(message, self.group_address, self.return_address)
	return GLARING

def ConnectToAddress_GLARING_GlareTimer(self, message):
	connect(self, self.ipp, session=self.session)
	self.attempts += 1
	return PENDING

def ConnectToAddress_GLARING_Stop(self, message):
	# Drop GlareTimer
	self.complete(ar.Aborted())

# CLOSING
def ConnectToAddress_CLOSING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CLOSING

def ConnectToAddress_CLOSING_Abandoned(self, message):
	# Terminated by remote before close could get through.
	self.complete(message)

def ConnectToAddress_CLOSING_Closed(self, message):
	# Completion of CONNECTED-Stop.
	self.complete(message.value)

CONNECT_TO_ADDRESS_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Connected, NotConnected, ar.Stop), ()
	),
	CONNECTED: (
		(ar.Unknown, Abandoned, ar.Stop, Closed), ()
	),
	GLARING: (
		(ar.Unknown, GlareTimer, ar.Stop), ()
	),
	CLOSING: (
		(ar.Unknown, Abandoned, Closed), ()
	),
}

ar.bind(ConnectToAddress, CONNECT_TO_ADDRESS_DISPATCH)

#
#
LISTEN_RETRY = ar.RetryIntervals(first_steps=[], regular_steps=4.0, randomized=0.25)

class ListenAtAddress(ar.Point, ar.StateMachine):
	def __init__(self, ipp, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.ipp = ipp
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.listening = None
		self.accepted = {}

		self.closing = None
		self.retry = None

	def reschedule(self):
		if self.retry is None:
			self.retry = ar.smart_intervals(LISTEN_RETRY)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def ListenAtAddress_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()
	listen(self, self.ipp, session=self.session)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of connect.
# Transport established.
def ListenAtAddress_PENDING_Listening(self, message):
	self.listening = message
	self.remote = self.return_address

	# Ready to accept
	self.send(UseAddress(self.address), self.parent_address)
	return ACCEPTING

def ListenAtAddress_PENDING_NotListening(self, message):
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ListenAtAddress_PENDING_Stop(self, message):
	# Local termination.
	# Listening could be orphaned here.
	self.complete(ar.Aborted())

# ACCEPTING
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def ListenAtAddress_ACCEPTING_Accepted(self, message):
	# Start of a session.
	# Are there intended to be others?
	self.accepted[self.return_address] = message

	self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def ListenAtAddress_ACCEPTING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return ACCEPTING

def ListenAtAddress_ACCEPTING_Abandoned(self, message):
	a = self.accepted.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def ListenAtAddress_ACCEPTING_Closed(self, message):
	a = self.accepted.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def ListenAtAddress_ACCEPTING_Stop(self, message):
	if len(self.accepted) == 0:
		self.complete(ar.Aborted())

	e = ar.Stop() if self.session else Close(ar.Aborted())

	for k, v in self.accepted.items():
		self.send(e, k)
	return CLOSING

# GLARING
# After a failed attempt or after abandoned.
def ListenAtAddress_GLARING_Unknown(self, message):
	# Non-control message sneaking through.
	self.forward(message, self.group_address, self.return_address)
	return GLARING

def ListenAtAddress_GLARING_GlareTimer(self, message):
	listen(self, self.ipp, session=self.session)
	self.attempts += 1
	return PENDING

def ListenAtAddress_GLARING_Stop(self, message):
	# Drop GlareTimer
	self.complete(ar.Aborted())

# CLOSING
def ListenAtAddress_CLOSING_Abandoned(self, message):
	a = self.accepted.pop(self.return_address, None)
	if a and len(self.accepted) > 0:
		return CLOSING
	self.complete(message)

def ListenAtAddress_CLOSING_Closed(self, message):
	a = self.accepted.pop(self.return_address, None)
	if a and len(self.accepted) > 0:
		return CLOSING
	self.complete(message)

LISTEN_AT_ADDRESS_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Listening, NotListening, ar.Stop), ()
	),
	ACCEPTING: (
		(Accepted, ar.Unknown, Abandoned, Closed, ar.Stop), ()
	),
	GLARING: (
		(ar.Unknown, GlareTimer, ar.Stop), ()
	),
	CLOSING: (
		(Abandoned, Closed), ()
	),
}

ar.bind(ListenAtAddress, LISTEN_AT_ADDRESS_DISPATCH)

#
# Subscribe/Publish
class SubscribeToListing(ar.Point, ar.StateMachine):
	def __init__(self, listing, scope=ScopeOfService.WAN, keep_connected=True, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.listing = listing
		self.scope = scope
		self.keep_connected = keep_connected
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.subscribed = None
		self.available = None
		self.remote = None

		self.closing = None
		self.intervals = None
		self.retry = None

	def reschedule(self):
		if self.intervals is None:
			s = local_private_public(self.ipp.host)
			r = ip_retry(s)
			self.intervals = r
		
		if self.retry is None:
			self.retry = ar.smart_intervals(self.intervals)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def SubscribeToListing_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()
	subscribe(self, self.listing, create_session=self.session, declared_scope=self.scope)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of subscibe.
# Subscription acknowledged.
def SubscribeToListing_PENDING_Subscribed(self, message):
	self.subscribed = message
	return READY

def SubscribeToListing_PENDING_NotSubscribed(self, message):
	self.complete(message)

def SubscribeToListing_PENDING_Stop(self, message):
	# Local termination.
	# Subscribed could be orphaned here.
	self.complete(ar.Aborted())

# READY
# Waiting for availability.
# Subscription acknowledged.
def SubscribeToListing_READY_Available(self, message):
	self.available = message
	self.remote = self.return_address

	# Remote object is ready.
	self.send(UseAddress(self.return_address), self.parent_address)
	return CONNECTED

def SubscribeToListing_READY_Stop(self, message):
	retract(self)
	self.complete(ar.Aborted())

# CONNECTED
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def SubscribeToListing_CONNECTED_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CONNECTED

def SubscribeToListing_CONNECTED_Dropped(self, message):
	# Normal end of a session.
	# Are there intended to be others?
	self.send(NoAddress(), self.parent_address)
	if self.keep_connected:
		return READY

	# End of session and only wanted 1.
	self.complete(message)

def SubscribeToListing_CONNECTED_Cleared(self, message):
	# Normal end of a session.
	# Are there intended to be others?
	self.send(NoAddress(), self.parent_address)
	if self.keep_connected:
		return READY

	# End of session and only wanted 1.
	self.complete(message.value)

def SubscribeToListing_CONNECTED_Stop(self, message):
	# This object ended by app. Take that as
	# signal to end this session and not activate retries.

	self.complete(ar.Aborted())

	#e = ar.Stop() if self.session else Close(ar.Aborted())

	#self.send(e, self.remote)
	#return CLOSING

# CLOSING
def SubscribeToListing_CLOSING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CLOSING

def SubscribeToListing_CLOSING_Abandoned(self, message):
	# Terminated by remote before close could get through.
	retract(self)
	self.complete(message)

def SubscribeToListing_CLOSING_Closed(self, message):
	# Completion of CONNECTED-Stop.
	retract(self)
	self.complete(message.value)

SUBSCRIBE_TO_LISTING_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Subscribed, ar.Stop), ()
	),
	READY: (
		(Available, ar.Stop), ()
	),
	CONNECTED: (
		(ar.Unknown, Dropped, Cleared, ar.Stop), ()
	),
	CLOSING: (
		(ar.Unknown, Abandoned, Closed), ()
	),
}

ar.bind(SubscribeToListing, SUBSCRIBE_TO_LISTING_DISPATCH)

#
#
class PublishAListing(ar.Point, ar.StateMachine):
	def __init__(self, listing, scope=ScopeOfService.WAN, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.listing = listing
		self.scope = scope
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.published = None
		self.delivered = {}

		self.closing = None
		self.retry = None

	def reschedule(self):
		if self.retry is None:
			self.retry = ar.smart_intervals(LISTEN_RETRY)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def PublishAListing_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()
	publish(self, self.listing, create_session=self.session, declared_scope=self.scope)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of publish.
# Listing established.
def PublishAListing_PENDING_Published(self, message):
	self.published = message

	# Ready to accept
	self.send(UseAddress(self.address), self.parent_address)
	return ACCEPTING

def PublishAListing_PENDING_NotPublished(self, message):
	self.complete(message)

def PublishAListing_PENDING_Stop(self, message):
	# Local termination.
	retract(self)
	self.complete(ar.Aborted())

# ACCEPTING
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def PublishAListing_ACCEPTING_Delivered(self, message):
	# Start of a session.
	# Are there intended to be others?
	self.delivered[self.return_address] = message

	self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def PublishAListing_ACCEPTING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return ACCEPTING

def PublishAListing_ACCEPTING_Dropped(self, message):
	a = self.delivered.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def PublishAListing_ACCEPTING_Cleared(self, message):
	a = self.delivered.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def PublishAListing_ACCEPTING_Stop(self, message):
	retract(self)
	self.complete(ar.Aborted())
	#if len(self.delivered) == 0:
	#	retract(self)
	#	self.complete(ar.Aborted())
	#
	#e = ar.Stop() if self.session else Close(ar.Aborted())
	#
	#for k, v in self.delivered.items():
	#	self.send(e, k)
	#return CLOSING

# CLOSING
def PublishAListing_CLOSING_Dropped(self, message):
	a = self.delivered.pop(self.return_address, None)
	if a and len(self.delivered) > 0:
		return CLOSING
	retract(self)
	self.complete(message)

def PublishAListing_CLOSING_Cleared(self, message):
	a = self.delivered.pop(self.return_address, None)
	if a and len(self.delivered) > 0:
		return CLOSING
	retract(self)
	self.complete(message)

PUBLISH_A_LISTING_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Published, NotPublished, ar.Stop), ()
	),
	ACCEPTING: (
		(Delivered, ar.Unknown, Dropped, Cleared, ar.Stop), ()
	),
	CLOSING: (
		(Dropped, Cleared), ()
	),
}

ar.bind(PublishAListing, PUBLISH_A_LISTING_DISPATCH)

#
#
class SubscribeToSearch(ar.Point, ar.StateMachine):
	def __init__(self, search, scope=ScopeOfService.WAN, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.search = search
		self.scope = scope
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.subscribed = None
		self.available = {}

		self.closing = None
		self.retry = None

	def reschedule(self):
		if self.retry is None:
			self.retry = ar.smart_intervals(LISTEN_RETRY)

		try:
			p = next(self.retry)
		except StopIteration:
			self.retry = None
			return False
	
		self.start(GlareTimer, p)
		return True

# INITIAL
# Launch this object.
def SubscribeToSearch_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()
	subscribe(self, self.search, create_session=self.session, declared_scope=self.scope)
	self.attempts = 1
	return PENDING

# PENDING
# Waiting for results of publish.
# Listing established.
def SubscribeToSearch_PENDING_Subscribed(self, message):
	self.subscribed = message

	# Ready to accept
	self.send(UseAddress(self.address), self.parent_address)
	return ACCEPTING

def SubscribeToSearch_PENDING_NotSubscribed(self, message):
	self.complete(message)

def SubscribeToSearch_PENDING_Stop(self, message):
	# Local termination.
	retract(self)
	self.complete(ar.Aborted())

# ACCEPTING
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def SubscribeToSearch_ACCEPTING_Available(self, message):
	# Start of a session.
	# Are there intended to be others?
	self.available[self.return_address] = message

	self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def SubscribeToSearch_ACCEPTING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return ACCEPTING

def SubscribeToSearch_ACCEPTING_Dropped(self, message):
	a = self.available.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def SubscribeToSearch_ACCEPTING_Cleared(self, message):
	a = self.available.pop(self.return_address, None)
	if a:
		self.forward(message, self.parent_address, self.return_address)
	return ACCEPTING

def SubscribeToSearch_ACCEPTING_Stop(self, message):
	retract(self)
	self.complete(ar.Aborted())
	#if len(self.available) == 0:
	#	retract(self)
	#	self.complete(ar.Aborted())
	#
	#e = ar.Stop() if self.session else Close(ar.Aborted())
	#
	#for k, v in self.available.items():
	#	self.send(e, k)
	#return CLOSING

# CLOSING
def SubscribeToSearch_CLOSING_Dropped(self, message):
	a = self.available.pop(self.return_address, None)
	if a and len(self.available) > 0:
		return CLOSING
	retract(self)
	self.complete(message)

def SubscribeToSearch_CLOSING_Cleared(self, message):
	a = self.available.pop(self.return_address, None)
	if a and len(self.available) > 0:
		return CLOSING
	retract(self)
	self.complete(message)

SUBSCRIBE_TO_SEARCH_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(Subscribed, ar.Stop), ()	# NotSubscribed?!
	),
	ACCEPTING: (
		(Available, ar.Unknown, Dropped, Cleared, ar.Stop), ()
	),
	CLOSING: (
		(Dropped, Cleared), ()
	),
}

ar.bind(SubscribeToSearch, SUBSCRIBE_TO_SEARCH_DISPATCH)
