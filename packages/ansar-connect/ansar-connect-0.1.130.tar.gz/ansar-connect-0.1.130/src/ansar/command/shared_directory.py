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
'''A network fixture that creates directories for connected clients.

Rather than a unique network address (IP + port) per directory, this
process uses a single address while managing multiple directories. Multiple
deployments of different products or different instances of the same
product can be supported.
'''
import ansar.connect as ar
from ansar.connect.wan import *
from ansar.connect.product import *
from ansar.connect.directory import find_overlap

__all__ = [
	'main',
]

# All the states for all the machines in
# this module.
class INITIAL: pass
class STARTING: pass
class READY: pass
class CLEARING: pass

CONNECT_ABOVE_TABLE = ar.MapOf(ar.Unicode(), ar.Any())

# The process object.
#
class ProductDirectory(ar.Threaded, ar.StateMachine):
	def __init__(self, settings):
		ar.Threaded.__init__(self)
		ar.StateMachine.__init__(self, INITIAL)
		self.settings = settings
		self.public_access = None		# This fixture listens here.
		self.accepted = {}				# Connected clients.
		self.directory = {}				# Directory per product+instance.
		self.connect_above = {}			# Upward link per product+instance.
		self.child_of = {}			# Sub-directories to directory.
		self.model = None				# File storage of connect_above.
		self.store = None				# Storage methods.
		self.recover = None

def ProductDirectory_INITIAL_Start(self, message):
	model = ar.object_model_folder()
	if model is None:
		self.complete(ar.Failed(model_load=(None, 'no model storage')))

	self.model = model.file('connect-above', CONNECT_ABOVE_TABLE, create_default=True)

	# Custom I/O routines.
	def store(connect_above=None):
		connect_above = connect_above or self.connect_above
		self.model.store(connect_above)

	def recover():
		self.connect_above, _ = self.model.recover()
		return self.connect_above
	
	self.store = store
	self.recover = recover

	# Initial load.
	self.recover()

	ar.listen(self, self.settings.public_access)
	return STARTING

# Verify access
def ProductDirectory_STARTING_Listening(self, message):
	self.public_access = message
	return READY

def ProductDirectory_STARTING_NotListening(self, message):
	# Something wrong. Bail.
	self.complete(ar.Faulted('No public access for product/instance', message.error_text))

def ProductDirectory_STARTING_Stop(self, message):
	# External intervention.
	self.complete(ar.Aborted())

# Connections from IP clients.
def ProductDirectory_READY_Accepted(self, message):
	# Need to remember connection details for full
	# operation of directories. Accepted messages
	# will be forwarded later to appropriate
	# directories.
	r = self.return_address[-1]
	self.accepted[r] = message

	self.trace(f'Accepted child [{r}] ({message.accepted_ipp})')
	return READY

def ProductDirectory_READY_Abandoned(self, message):
	# Need to generate abandon messages for the
	# relevant directories.
	r = self.return_address[-1]
	p = self.accepted.pop(r, None)
	if p is None:
		self.warning(f'Abandoned by unknown child [{r}]')
		return READY

	hap = str(p.accepted_ipp)
	d = self.child_of.pop(r, None)
	if d is None:
		self.trace(f'Abandoned by child [{r}] ({hap}), not registered as sub-directory')
		return READY

	self.forward(message, d, self.return_address)
	self.trace(f'Abandoned by child [{r}] ({hap})')

	return READY

def ProductDirectory_READY_Closed(self, message):
	# Need to generate abandon messages for the
	# relevant directories.
	r = self.return_address[-1]
	p = self.accepted.pop(r, None)
	if p is None:
		self.warning(f'Close of unknown child [{r}]')
		return READY

	hap = str(p.accepted_ipp)
	d = self.child_of.pop(r, None)
	if d is None:
		self.trace(f'Close of child [{r}] ({hap})" (not registered as sub-directory')
		return READY

	self.forward(message, d, self.return_address)
	self.trace(f'Close of child [{r}] ({hap})')

	return READY

def ProductDirectory_READY_ProductLookup(self, message):
	r = self.return_address[-1]

	settings = self.settings

	product_name = message.product_name or 'acme'
	product_instance = message.product_instance or InstanceOfProduct.DEVELOPMENT
	k = f'{product_name}:{product_instance}'

	d = self.directory.get(k)
	if d is None:
		self.trace(f'Unknown directory key "{k}" for child [{r}]')
		c = self.connect_above.get(k)
		if c is None:
			self.trace(f'Unknown upward key "{k}" for child [{r}]')
			# Default upward access is disabled but a hint that it
			# should adopt the same nature.
			c = ProductAccess(product_name=product_name, product_instance=product_instance)
			self.connect_above[k] = c
			self.store()

		d = self.create(ar.ServiceDirectory,
			scope=settings.directory_scope,			# All at same scope.
			connect_above=c,
			accept_below=ar.HostPort())				# Disabled.

		self.assign(d, k)
		self.directory[k] = d

	self.child_of[r] = d
	accepted = self.accepted.get(r)
	if accepted:
		self.forward(accepted, d, self.return_address)
	else:
		self.trace(f'Not an accepted child [{r}]')
	self.reply(YourProduct(d))
	return READY

def ProductDirectory_READY_HostPort(self, message):
	# Consume the redundant message. Listening by
	# all directories is disabled, so host-port
	# is empty.
	return READY

def ProductDirectory_READY_Anything(self, message):
	connect_above = message.thing

	if not isinstance(connect_above, (ProductAccess, WideAreaAccess)):
		t = ar.tof(connect_above)
		self.warning(f'Attempt to connect up to "{t}" from a product directory')
		self.reply(ar.Ack())
		return READY

	k = self.progress()
	if k is None:
		self.warning(f'Attempt to connect up from an unknown directory')
		self.reply(ar.Ack())
		return READY

	self.connect_above[k] = connect_above
	self.store()

	self.reply(ar.Ack())
	return READY

def ProductDirectory_READY_Completed(self, message):
	k = self.debrief()
	d = self.directory.pop(k, None)
	if d is None:
		self.warning(f'Termination of unknown object')
		return READY
	self.warning(f'Termination of directory "{k}", tearing down')
	
	# A directory has died. Force any sub-directories
	# to re-connect and thereby create a new
	# instance.
	c = []
	for s, v in self.child_of.items():
		if v == d:
			self.send(ar.Close(), (s,))
			c.append(s)

	for t in c:
		self.child_of.pop(t, None)
	return READY

def ProductDirectory_READY_Stop(self, message):
	if self.working():
		self.abort()
		return CLEARING
	self.complete(ar.Ack())

def ProductDirectory_CLEARING_Completed(self, message):
	self.debrief()
	if self.working():
		return CLEARING
	self.complete(ar.Ack())

PRODUCT_DIRECTORY_DISPATCH = {
    INITIAL: (
        (ar.Start,), ()
    ),
    STARTING: (
        (ar.Listening, ar.NotListening, ar.Stop), ()
    ),
    READY: (
        (ar.Accepted, ar.Abandoned, ar.Closed,
		ProductLookup, ar.HostPort,
		ar.Anything,
		ar.Completed,
		ar.Stop), ()
    ),
    CLEARING: (
        (ar.Completed), ()
    ),
}

ar.bind(ProductDirectory, PRODUCT_DIRECTORY_DISPATCH)


# Allow configuration of network details.
#
class Settings(object):
	def __init__(self, directory_scope=None, public_access=None):
		self.directory_scope = directory_scope
		self.public_access = public_access or ar.HostPort()

SETTINGS_SCHEMA = {
	'directory_scope': ar.ScopeOfService,
	'public_access': ar.UserDefined(ar.HostPort),
}

ar.bind(Settings, object_schema=SETTINGS_SCHEMA)

#
#
factory_settings = Settings(directory_scope=ar.ScopeOfService.HOST,
	public_access=ar.LocalPort(32177))

#
#
def main():
    ar.create_object(ProductDirectory, factory_settings=factory_settings)

# The standard entry point. Needed for IDEs
# and debugger sessions.
if __name__ == '__main__':
    main()
