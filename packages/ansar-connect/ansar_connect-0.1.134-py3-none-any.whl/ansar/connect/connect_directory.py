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
from .networking_if import *
from .product import *
from .wan import *
from .plumbing import ip_retry

__all__ = [
	'ConnectToDirectory',
]

#
#
class INITIAL: pass
class DISABLED: pass
class PENDING: pass
class CONNECTED: pass
class PRODUCING: pass
class GLANCING: pass
class CLOUDY: pass
class LOOKING: pass
class RECONNECTING: pass
class GLARING: pass
class CONNECTING: pass
class REDIRECTING: pass
class ASSIGNING: pass
class CLOSING: pass

class ConnectToDirectory(ar.Point, ar.StateMachine):
	def __init__(self, connect_above, session=None, group_address=None):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.connect_above = connect_above
		self.session = session
		self.group_address = group_address

		self.started = None
		self.attempts = 0

		self.connected = None
		self.remote = None
		self.redirect = None

		self.closing = None
		self.intervals = None
		self.retry = None

	def connect(self):
		c = self.connect_above
		if isinstance(c, HostPort):
			ipp = c
			next = PENDING
		elif isinstance(c, ProductAccess):
			ipp = c.access_ipp
			next = PRODUCING
		elif isinstance(c, WideAreaAccess):
			ipp = c.access_ipp
			next = CLOUDY
		else:
			return DISABLED

		if ipp.host is None:
			return DISABLED
		connect(self, ipp, session=self.session)
		self.start(ar.T1, seconds=8.0)
		return next

	def reschedule(self):
		if self.intervals is None:
			c = self.connect_above
			if isinstance(c, HostPort):
				ipp = c
			elif isinstance(c, ProductAccess):
				ipp = c.access_ipp
			elif isinstance(c, WideAreaAccess):
				ipp = c.access_ipp
			else:
				ipp = None

			if ipp is None or ipp.host is None:
				s = ScopeOfIP.PUBLIC
			else:
				s = local_private_public(ipp.host)
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
def ConnectToDirectory_INITIAL_Start(self, message):
	self.group_address = self.group_address or self.parent_address

	# Start from nothing.
	self.started = ar.world_now()

	self.attempts = 1
	return self.connect()

# DISABLED
def ConnectToDirectory_DISABLED_Anything(self, message):
	self.connect_above = message.thing
	self.attempts = 1
	return self.connect()

def ConnectToDirectory_DISABLED_Stop(self, message):
	self.complete(ar.Aborted())

# PENDING (HostPort)
# Waiting for results of connect.
# Transport established.
def ConnectToDirectory_PENDING_Connected(self, message):
	self.cancel(ar.T1)
	self.connected = message
	self.remote = self.return_address

	# Remote object is ready.
	self.send(UseAddress(self.remote), self.parent_address)
	return CONNECTED

def ConnectToDirectory_PENDING_NotConnected(self, message):
	self.send(message, self.parent_address)
	self.cancel(ar.T1)
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_PENDING_T1(self, message):
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_PENDING_Stop(self, message):
	# Local termination.
	# Connected could be orphaned here.
	self.complete(ar.Aborted())

# PRODUCING (ProductAccess)
# Waiting for results of connect.
# Transport established.
def ConnectToDirectory_PRODUCING_Connected(self, message):
	self.cancel(ar.T1)
	self.connected = message

	c = self.connect_above
	lookup = ProductLookup(c.product_name, c.product_instance)
	self.reply(lookup)
	return GLANCING

def ConnectToDirectory_PRODUCING_NotConnected(self, message):
	self.send(message, self.parent_address)
	self.cancel(ar.T1)
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_PRODUCING_T1(self, message):
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_PRODUCING_Stop(self, message):
	# Local termination.
	# Connected could be orphaned here.
	self.complete(ar.Aborted())

def ConnectToDirectory_GLANCING_YourProduct(self, message):
	self.remote = message.address
	# Remote object is ready.
	self.send(UseAddress(self.remote), self.parent_address)
	return CONNECTED

def ConnectToDirectory_GLANCING_Stop(self, message):
	self.send(ar.Close(ar.Aborted()), self.connected.remote_address)
	return CLOSING

# CLOUDY (WideAreaAccess)
# Waiting for results of connect.
# Transport established.
def ConnectToDirectory_CLOUDY_Connected(self, message):
	self.cancel(ar.T1)
	self.connected = message

	c = self.connect_above
	lookup = WideAreaLookup(account_id=c.account_id, directory_id=c.directory_id)
	self.reply(lookup)
	self.start(ar.T2, seconds=4.0)
	return LOOKING

def ConnectToDirectory_CLOUDY_NotConnected(self, message):
	self.send(message, self.parent_address)
	self.cancel(ar.T1)
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_CLOUDY_T1(self, message):
	# Attempt failed.
	# No session and no change of status for owner.
	# Schedule another or perhaps end of attempts.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_CLOUDY_Stop(self, message):
	# Local termination.
	# Connected could be orphaned here.
	self.complete(ar.Aborted())

def ConnectToDirectory_LOOKING_WideAreaRedirect(self, message):
	self.redirect = message
	ipp = message.redirect_ipp
	self.trace(f'Redirecting from FOH to WAN ({ipp})')
	connect(self, ipp)
	self.reply(Close())
	return REDIRECTING

def ConnectToDirectory_LOOKING_T2(self, message):
	value = ar.TimedOut(message)
	self.send(Close(value), self.connected.remote_address)
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_LOOKING_Stop(self, message):
	self.send(Close(ar.Aborted()), self.connected.remote_address)
	return CLOSING

def ConnectToDirectory_REDIRECTING_Connected(self, message):
	self.connected = message
	r = self.redirect
	assignment = WideAreaAssignment(r.directory_id, r.assignment_token)
	self.reply(assignment)
	return ASSIGNING

def ConnectToDirectory_REDIRECTING_NotConnected(self, message):
	self.send(message, self.parent_address)
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_REDIRECTING_T2(self, message):
	# Dropped the original connection and redirect not
	# successful.
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_REDIRECTING_Stop(self, message):
	self.complete(ar.Aborted())

def ConnectToDirectory_ASSIGNING_YourWideArea(self, message):
	self.cancel(ar.T2)
	self.remote = message.address
	# Remote object is ready.
	self.send(UseAddress(self.remote), self.parent_address)
	return CONNECTED

def ConnectToDirectory_ASSIGNING_Closed(self, message):
	# Housekeeping - dropped previous connection.
	return ASSIGNING

def ConnectToDirectory_ASSIGNING_Unknown(self, message):
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_ASSIGNING_T2(self, message):
	value = ar.TimedOut(message)
	self.send(Close(value), self.connected.remote_address)
	if self.reschedule():
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_ASSIGNING_Stop(self, message):
	self.complete(ar.Aborted())

# GLARING
# After a failed attempt or after abandoned.
def ConnectToDirectory_GLARING_Unknown(self, message):
	# Non-control message sneaking through.
	self.forward(message, self.group_address, self.return_address)
	return GLARING

def ConnectToDirectory_GLARING_Anything(self, message):
	self.connect_above = message.thing
	self.attempts = 1
	return self.connect()

def ConnectToDirectory_GLARING_GlareTimer(self, message):
	self.attempts += 1
	return self.connect()

def ConnectToDirectory_GLARING_Stop(self, message):
	# Drop GlareTimer
	self.complete(ar.Aborted())

# CONNECTED
# Caretaker role. Pass app messages on to owner
# and wait for further control messages.
def ConnectToDirectory_CONNECTED_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CONNECTED

def ConnectToDirectory_CONNECTED_Anything(self, message):
	self.connect_above = message.thing
	self.send(Close(), self.remote)
	return RECONNECTING

def ConnectToDirectory_CONNECTED_Abandoned(self, message):
	# Start the retries up again.
	self.started = ar.world_now()
	self.attempts = 0
	self.retry = None
	if self.reschedule():
		# Update the owner that the current session
		# is over.
		self.send(NoAddress(), self.parent_address)
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_CONNECTED_Stop(self, message):
	# This object ended by app. Take that as
	# signal to end this session and not activate retries.

	e = ar.Stop() if self.session else Close(ar.Aborted())

	self.send(e, self.remote)
	return CLOSING

def ConnectToDirectory_CONNECTED_Closed(self, message):
	# Local end has sent close to the proxy. Treat this
	# as a short-circuit version of above.
	self.complete(message.value)

#
#
def ConnectToDirectory_RECONNECTING_Abandoned(self, message):
	# Start the retries up again.
	self.started = ar.world_now()
	self.attempts = 0
	self.retry = None
	if self.reschedule():
		self.send(NoAddress(), self.parent_address)
		return GLARING

	x = ar.Exhausted(message, attempts=self.attempts, started=self.started)
	self.complete(x)

def ConnectToDirectory_RECONNECTING_Closed(self, message):
	return ConnectToDirectory_RECONNECTING_Abandoned(self, message)

def ConnectToDirectory_RECONNECTING_Stop(self, message):
	return CLOSING

# CLOSING
def ConnectToDirectory_CLOSING_Unknown(self, message):
	# Normal operation.	Forward app message on to proper target.
	self.forward(message, self.group_address, self.return_address)
	return CLOSING

def ConnectToDirectory_CLOSING_Abandoned(self, message):
	# Terminated by remote before close could get through.
	self.complete(message)

def ConnectToDirectory_CLOSING_Closed(self, message):
	# Completion of CONNECTED-Stop.
	self.complete(message.value)

CONNECT_TO_DIRECTORY_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	DISABLED: (
		(ar.Anything, ar.Stop), ()
	),
	PENDING: (
		(Connected, NotConnected, ar.T1, ar.Stop), (ar.Anything,)
	),
	PRODUCING: (
		(Connected, NotConnected, ar.T1, ar.Stop), (ar.Anything,)
	),
	GLANCING: (
		(YourProduct, ar.Stop), (ar.Anything,)
	),
	CLOUDY: (
		(Connected, NotConnected, ar.T1, ar.Stop), (ar.Anything,)
	),
	LOOKING: (
		(WideAreaRedirect, ar.T2, ar.Stop), (ar.Anything,)
	),
	REDIRECTING: (
		(Connected, NotConnected, ar.T2, ar.Stop), (ar.Anything,)
	),
	ASSIGNING: (
		(YourWideArea, Closed, ar.Unknown, ar.T2, ar.Stop), (ar.Anything,)
	),
	GLARING: (
		(ar.Unknown, ar.Anything, GlareTimer, ar.Stop), ()
	),
	CONNECTED: (
		(ar.Unknown, ar.Anything, Abandoned, Closed, ar.Stop), ()
	),
	RECONNECTING: (
		(Closed, Abandoned, ar.Stop), ()
	),
	CLOSING: (
		(ar.Unknown, Abandoned, Closed), ()
	),
}

ar.bind(ConnectToDirectory, CONNECT_TO_DIRECTORY_DISPATCH)
