# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2017-2024 Scott Woods
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
'''.

.
'''
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *
from .transporting import *
from .plumbing import *
from .networking_if import *

__all__ = [
	'GroupTable',
	'GroupUpdate',
	'AddressGroup',
	'GroupObject',
]

# The specification.
class GroupTable(object):
	def __init__(self, **member_frame):
		if 'member_frame' in member_frame or 'create' in member_frame or 'update' in member_frame:
			raise ValueError('names of members would hide GroupTable methods')
		self.member_frame = member_frame

	def create(self, owner, get_ready=None, session=None, resident_code=False, until_stopped=False):
		for k in self.member_frame.keys():
			setattr(self, k, None)	# Fill with blanks.
		a = owner.create(AddressGroup, self.member_frame, session=session, resident_code=resident_code, get_ready=get_ready, until_stopped=until_stopped)
		return a

	def update(self, message):
		if message.key in self.member_frame:
			setattr(self, message.key, message.address)

# Runtime image.
class GroupUpdate(object):
	def __init__(self, key=None, address=None):
		self.key = key
		self.address = address

UPDATE_GROUP_SCHEMA = {
	'key': ar.Unicode(),
	'address': ar.Address(),
}

ar.bind(GroupUpdate, object_schema=UPDATE_GROUP_SCHEMA)

# Dedicated timers.
class GroupTimer(object): pass

ar.bind(GroupTimer)

class Group(object): pass

#
#
class INITIAL: pass
class PENDING: pass
class LATCHING: pass
class READY: pass
class RESTARTING: pass
class UNLATCHING: pass
class CLEARING: pass
class RUNNING: pass

LATCH_ID = 1
SESSION_ID = 2

class AddressGroup(ar.Point, ar.StateMachine):
	def __init__(self, table, session=None, resident_code=False, get_ready=None, until_stopped=False):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.table = table						# Rows of CreateFrames.
		self.session = session					# The object to be created or null.
		self.resident_code = resident_code		# Is this an endless series of sessions.
		self.get_ready = get_ready				# Limit the setup time.
		self.until_stopped = until_stopped		# Termination by intervention, i.e. command?

		self.latch = None		# Temporary address while pending.
		self.created = None		# Address of the session.

		self.ready = Group()			# The set of runtime addresses.
		self.return_value = None		# Hold the value for final complete.
		self.session_value = None		# Pass completion value from one session to the next.


# START
# Start each of the member objects. If appropriate, create a
# temporary address to capture messages from objects that are
# ready before the group is ready.
def AddressGroup_INITIAL_Start(self, message):
	if not self.table:
		self.complete(ar.Faulted('empty table', 'a group with no members has nothing to do'))

	if not self.resident_code and self.get_ready is not None:
		self.start(GroupTimer, self.get_ready)

	if self.session:
		self.latch = self.create(ar.Latch, '', self.parent_address)
		self.assign(self.latch, LATCH_ID)

	for k, v in self.table.items():
		setattr(self.ready, k, None)
		a = self.create(v.object_type, *v.args, group_address=self.latch, **v.kw)
		self.assign(a, k)
	
	return PENDING

# PENDING
# Assumption is that eventually all members will provide a runtime
# address and the whole group will go ready. Which is the moment
# a session is created.
def AddressGroup_PENDING_UseAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	a = getattr(self.ready, k, None)
	if a:
		self.warning(f'Table entry "{k}" already on record (ignored)')
		return PENDING

	setattr(self.ready, k, message.address)
	def ready():
		for k in self.table.keys():
			a = getattr(self.ready, k, None)
			if a is None:
				return False
		return True

	r = ready()
	if not self.session:
		# Owner expects notification stream. Add the
		# new address and provide trailing edge of
		# READY event.
		self.send(GroupUpdate(k, message.address), self.parent_address)
		if r: 
			self.send(ar.Ready(), self.parent_address)
			return READY
		return PENDING

	if r:
		# Use the factory to create a new session object passing the
		# object of addresses. Use distinct call signature for create()
		# to avoid imposing session_value=None on every group object.
		c = self.session
		if self.session_value is None:
			a = self.create(c.object_type, self.ready, *c.args, **c.kw)
		else:
			a = self.create(c.object_type, self.ready, *c.args, session_value=self.session_value, **c.kw)
		self.assign(a, SESSION_ID)
		self.created = a
		# Get latch to work the address magic so that session
		# receives potentially crucial messages from members.
		self.send(ar.SwitchOver(a), self.latch)
		return LATCHING

	return PENDING

def AddressGroup_PENDING_NoAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	a = getattr(self.ready, k, None)
	if a is None:
		self.warning(f'Table entry "{k}" was not on record')
		return PENDING

	setattr(self.ready, k, None)

	if not self.session:
		self.send(GroupUpdate(k, None), self.parent_address)

	return PENDING

def AddressGroup_PENDING_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return PENDING

	# All permutations of group terminate if any member
	# drops out.
	if isinstance(k, str):
		a = getattr(self.ready, k, None)

		if not self.session and a:
			self.send(GroupUpdate(k, None), self.parent_address)

	if self.working():
		self.return_value = message.value
		self.abort()
		return CLEARING

	self.complete(message.value)

def AddressGroup_PENDING_GroupTimer(self, message):
	self.return_value = ar.TimedOut(message)
	self.abort()
	return CLEARING

def AddressGroup_PENDING_Stop(self, message):
	self.return_value = ar.Aborted()
	self.abort()
	return CLEARING

# LATCHING
# The group is going ready, just need confirmation
# that latching has worked. Use that message to
# rewire the "assigned job" machinery.
def AddressGroup_LATCHING_Ack(self, message):
	j = self.address_job.pop(self.latch, None)
	if j != LATCH_ID:
		self.return_value = ar.Faulted('Ack but not the assigned latch', 'internal')
		self.warning(f'{self.group_value}')
		self.abort()
		return CLEARING
	self.assign(self.return_address, LATCH_ID)		# Latch has been re-homed to this new address.
	self.latch = self.return_address
	return READY

def AddressGroup_LATCHING_Unknown(self, message):
	self.save(message)
	return LATCHING

def AddressGroup_LATCHING_Stop(self, message):
	self.return_value = ar.Aborted()
	self.abort()
	return CLEARING

# READY
# The session object is running, presumably sending and
# receiving from the group of runtime messages.
def AddressGroup_READY_NoAddress(self, message):
	k = self.progress()
	if k is None:
		self.warning(f'Unknown sender {self.return_address}')
		return READY

	a = getattr(self.ready, k, None)
	if a is None:
		self.warning(f'Table entry "{k}" was not on record')
		return READY

	# Lost the READY status.
	setattr(self.ready, k, None)

	if not self.session:
		# Owner wants notication stream.
		# Delete the named address and provide leading
		# edge "not ready" event. Back to PENDING state.
		self.send(ar.NotReady(), self.parent_address)
		self.send(GroupUpdate(k, None), self.parent_address)
		return PENDING

	if self.resident_code:
		# This group is here for the long run. Terminate
		# the session.
		self.send(ar.Stop(), self.created)
		return RESTARTING

	# This code terminates at the end of the ready state.
	if self.working():
		self.return_value = ar.Faulted(f'Lost address "{k}" in group session', 'group no longer complete')
		self.abort()
		return CLEARING

	self.complete(message)

def AddressGroup_READY_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown address {self.return_address}')
		return PENDING

	if isinstance(k, str):
		if not self.session:
			# Leading edge notification.
			self.send(ar.NotReady(), self.parent_address)
			self.send(GroupUpdate(k, None), self.parent_address)
		self.return_value = message.value
	elif k == SESSION_ID:
		self.return_value = message.value
	elif k == LATCH_ID:
		self.return_value = message.value
	else:
		self.return_value = ar.Faulted(f'Address "{k}" completed and not member or id', 'internal')

	if self.working():
		self.abort()
		return CLEARING

	self.complete(self.return_value)

def AddressGroup_READY_Unknown(self, message):
	# Probably application message that needs to be
	# forwarded onto the proper object, i.e. the active
	# session of the owner of the group.
	if self.created:
		self.forward(message, self.created, self.return_address)
	else:
		self.forward(message, self.parent_address, self.return_address)
	return READY

def AddressGroup_READY_Stop(self, message):
	self.return_value = ar.Aborted()
	self.abort()
	return CLEARING

# RESTARTING
# Stopped the session and waiting for its
# termination.
def AddressGroup_RESTARTING_Completed(self, message):
	j = self.debrief()
	if j != SESSION_ID:
		self.return_value = ar.Faulted(f'Lost member "{j}" during restart', 'shift to termination')
		if self.working():
			self.abort()
			return CLEARING
		self.complete(self.group_value)

	# Save the value and pass to any subsequent
	# sessions.
	self.session_value = message.value

	# Session gone. Ask the latch to reclaim its
	# proper place.
	self.send(ar.Reclaim(), self.latch)
	return UNLATCHING

def AddressGroup_RESTARTING_Stop(self, message):
	self.return_value = ar.Aborted()
	self.abort()
	return CLEARING

# UNLATCHING
# Lost and address, dropped the session and now
# waiting for confirmation the latch is back in
# its proper place.
def AddressGroup_UNLATCHING_Ack(self, message):
	j = self.address_job.pop(self.latch, None)
	if j != LATCH_ID:
		self.return_value = ar.Faulted('Ack but not from the assigned latch', 'internal')
		self.warning(f'{self.group_value}')
		self.abort()
		return CLEARING
	self.assign(self.return_address, LATCH_ID)		# Latch has been restored to original address.
	self.latch = self.return_address
	return PENDING

def AddressGroup_UNLATCHING_Stop(self, message):
	self.return_value = ar.Aborted()
	self.abort()
	return CLEARING

# CLEARING
# This group is going down.
def AddressGroup_CLEARING_Completed(self, message):
	k = self.debrief()
	if k is None:
		self.warning(f'Unknown address {self.return_address}')
		return CLEARING

	if isinstance(k, str):
		if not self.session:
			self.send(GroupUpdate(k, None), self.parent_address)
	elif k == SESSION_ID:
		if isinstance(self.return_value, ar.Aborted) and self.until_stopped:
			self.return_value = message.value
	if self.working():
		return CLEARING

	self.complete(self.return_value)


ADDRESS_GROUP_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	PENDING: (
		(UseAddress, NoAddress, ar.Completed, GroupTimer, ar.Stop), ()
	),
	LATCHING: (
		(ar.Ack, ar.Unknown, ar.Stop), (NoAddress, ar.Completed)
	),
	READY: (
		(NoAddress, ar.Completed, ar.Unknown, ar.Stop), ()
	),
	RESTARTING: (
		(ar.Completed, ar.Stop), (NoAddress, UseAddress)
	),
	UNLATCHING: (
		(ar.Ack, ar.Stop), (ar.Completed, NoAddress, UseAddress)
	),
	CLEARING: (
		(ar.Completed,), ()
	),
}

ar.bind(AddressGroup, ADDRESS_GROUP_DISPATCH)

# A shim object between create_object() and the application object.
# This is the most concise way to run an object with the support
# of one or more runtime objects, e.g. a connection to a service.
class GroupObject(ar.Point, ar.StateMachine):
	def __init__(self, *args_plus_2, get_ready=None, resident_code=False, until_stopped=False):
		ar.Point.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		# Need to trampoline a variable list of settings, input and variables
		# onto the receiving function, i.e. group_args.
		self.args = args_plus_2[:-2]
		self.session = args_plus_2[-2]
		self.group_args = args_plus_2[-1]
		self.get_ready = get_ready
		self.resident_code = resident_code
		self.until_stopped = until_stopped

		self.group = None
		self.created = None
		self.closing = None

def GroupObject_INITIAL_Start(self, message):
	# Convert settings, input and variables into args and
	# kw suitable for the session object. This is all about
	# converting the "command-line" info its most useful
	# form.
	self.group, args, kv = self.group_args(*self.args)

	# Create a session factory.
	session = CreateFrame(self.session, *args, **kv)

	# Real work done by AddressGroup.
	# Create the group passing the factory for those moments
	# when the group goes ready.
	self.created = self.group.create(self, session=session, resident_code=self.resident_code, get_ready=self.get_ready, until_stopped=self.until_stopped)
	return RUNNING

def GroupObject_RUNNING_Completed(self, message):
	self.complete(message.value)

def GroupObject_RUNNING_Stop(self, message):
	self.send(message, self.created)
	return RUNNING

GROUP_SESSION_DISPATCH = {
	INITIAL: (
		(ar.Start,), ()
	),
	RUNNING: (
		(ar.Completed, ar.Stop), ()
	),
}

ar.bind(GroupObject, GROUP_SESSION_DISPATCH)
