# Author: Scott Woods <scott.18.ansar@gmail.com.com>
# MIT License
#
# Copyright (c) 2022, 2023 Scott Woods
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

""".

.
"""
__docformat__ = 'restructuredtext'

__all__ = [
	'NetworkSettings',
	'PingSettings',
	'AccountSettings',
	'DirectorySettings',
	'procedure_network',
	'procedure_ping',
	'procedure_signup',
	'procedure_login',
	'procedure_account',
	'procedure_directory',
]

import os
import getpass
import uuid
import ansar.connect as ar
from ansar.encode.args import QUOTED_TYPE, SHIPMENT_WITH_QUOTES, SHIPMENT_WITHOUT_QUOTES
from ansar.create.procedure import DEFAULT_HOME, DEFAULT_GROUP, HOME, GROUP
from ansar.create.procedure import open_home, role_status
from ansar.create.object import decoration_store
from ansar.connect.group_if import GroupSettings
from ansar.connect.standard import *
from .foh_if import *
from .wan import *
from .product import *
from .directory_if import *

DEFAULT_ACCOUNT_ACTION = 'show'

# Per-command arguments as required.
# e.g. command-line parameters specific to create.
class NetworkSettings(object):
	def __init__(self, group_name=None, home_path=None,
			connect_scope=None, to_scope=None,
			product_name=None, product_instance=None,
			custom_host=None, custom_port=None,
			reserved=False,
			connect_file=None, connect_disable=False,
			published_services=False, subscribed_searches=False, routed_matches=False, accepted_processes=False,
			host_and_port=False, start_time=False):
		self.group_name = group_name
		self.home_path = home_path
		self.connect_scope = connect_scope
		self.to_scope = to_scope
		self.product_name = product_name
		self.product_instance = product_instance
		self.custom_host = custom_host
		self.custom_port = custom_port
		self.reserved = reserved
		self.connect_file = connect_file
		self.connect_disable = connect_disable
		self.published_services = published_services
		self.subscribed_searches = subscribed_searches
		self.routed_matches = routed_matches
		self.accepted_processes = accepted_processes
		self.host_and_port = host_and_port
		self.start_time = start_time

NETWORK_SETTINGS_SCHEMA = {
	'group_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'connect_scope': ScopeOfService,
	'to_scope': ScopeOfService,
	'product_name': ar.Unicode(),
	'product_instance': InstanceOfProduct,
	'custom_host': ar.Unicode(),
	'custom_port': ar.Integer8(),
	'reserved': ar.Boolean(),
	'connect_file': ar.Unicode(),
	'connect_disable': ar.Boolean(),
	'published_services': ar.Boolean(),
	'subscribed_searches': ar.Boolean(),
	'routed_matches': ar.Boolean(),
	'accepted_processes': ar.Boolean(),
	'host_and_port': ar.Boolean(),
	'start_time': ar.Boolean(),
}

ar.bind(NetworkSettings, object_schema=NETWORK_SETTINGS_SCHEMA)

#
#
def lfa_text(d):
	f, l, a = len(d.listing), len(d.find), len(d.accepted)
	s = f'{f}/{l}/{a}'
	return s

def output_ancestry(self, ancestry, network):
	for d in reversed(ancestry.lineage):

		scope = ScopeOfService.to_name(d.scope) if d.scope else '?'
		if isinstance(d.connect_above, ar.HostPort):
			connecting_ipp = d.connect_above
			display_name = str(connecting_ipp)
		elif isinstance(d.connect_above, ProductAccess):
			connecting_ipp = d.connect_above.access_ipp
			e = InstanceOfProduct.to_name(d.connect_above.product_instance)
			display_name = f'{d.connect_above.product_name}/{e}'
		elif isinstance(d.connect_above, WideAreaAccess):
			connecting_ipp = d.connect_above.access_ipp
			display_name = f'{d.connect_above}'
		else:
			continue

		if connecting_ipp.host is None:
			continue

		started = ar.world_to_text(d.started) if d.started else '-'
		connected = ar.world_to_text(d.connected) if d.connected else '-'
		lfa = lfa_text(d)

		note = []
		if network.host_and_port:
			note.append(str(connecting_ipp))
		if network.start_time:
			note.append(started)

		if connecting_ipp.host is None:
			note.append('DISABLED')
		elif d.not_connected:
			note.append(d.not_connected)

		key_name = {k: r.search_or_listing for r in d.listing for k in r.route_key}
		if note:
			s = ', '.join(note)
			ar.output_line(f'+ {scope} {display_name} ({s})')
		else:
			ar.output_line(f'+ {scope} {display_name}')
		if network.published_services:
			ar.output_line(f'+ Published services ({len(d.listing)})', tab=1)
			for r in d.listing:
				ar.output_line(f'+ {r.search_or_listing} ({len(r.route_key)})', tab=2)
		if network.subscribed_searches:
			ar.output_line(f'+ Subscribed searches ({len(d.find)})', tab=1)
			for r in d.find:
				ar.output_line(f'+ {r.search_or_listing} ({len(r.route_key)})', tab=2)
				if network.routed_matches:
					for k in r.route_key:
						ar.output_line(f'+ "{key_name[k]}"', tab=3)
		if network.accepted_processes:
			ar.output_line(f'+ Accepted processes ({len(d.accepted)})', tab=1)
			for a in d.accepted:
				ar.output_line(f'+ {a}', tab=2)

def scope_host(scope):
	if scope == ar.ScopeOfService.HOST:
		return ANSAR_LOCAL_HOST
	elif scope == ar.ScopeOfService.LAN:
		return ANSAR_LAN_HOST
	return None

def procedure_network(self, network, group, home):
	group = ar.word_argument_2(group, network.group_name, DEFAULT_GROUP, GROUP)
	home = ar.word_argument_2(home, network.home_path, DEFAULT_HOME, HOME)

	if '.' in group:
		e = ar.Rejected(group_name=(group, f'no-dots name'))
		raise ar.Incomplete(e)
	group_role = f'group.{group}'

	hb = open_home(home)

	# if not hb.role_exists(group_role):
	#	e = ar.Failed(group_exists=(f'group "{group}" not found', None))
	#	raise ar.Incomplete(e)
	# TBD - auto-create or not.
	settings = GroupSettings()
	hr = hb.open_role(group_role, settings, None, ar.NodeProperties())

	_, running = role_status(self, hb, [group_role])
	if running:
		e = ar.Failed(group_running=(f'group "{group}" is already running', None))
		raise ar.Incomplete(e)

	settings = hr.role_settings[2]				# From the group.
	connect_above = settings.connect_above
	accept_below = ar.LocalPort(0)				# Grab an ephemeral for consistency.

	a = self.create(ar.ServiceDirectory, ar.ScopeOfService.GROUP, connect_above, accept_below)
	self.directory = a

	try:
		# Directory responds with a HostPort.
		m = self.select(ar.HostPort, ar.Stop)
		if isinstance(m, ar.HostPort):
			connect_above = m
	
		# Wait for a grace period.
		self.start(ar.T2, seconds=1.5)
		self.select(ar.T2, ar.Stop)

		# Look for expression of connect or default to scan.
		if network.connect_scope and network.to_scope:					# ProductAccess or HostPort
			connect_scope = network.connect_scope
			to_scope = network.to_scope
			if network.product_name and network.product_instance:		# ProductAccess
				shared_host = network.custom_host or scope_host(to_scope)
				shared_port = network.custom_port or ANSAR_SHARED_PORT
				access_ipp = ar.HostPort(shared_host, shared_port)
				connect_above= ProductAccess(access_ipp=access_ipp,
					product_name=network.product_name,
					product_instance=network.product_instance)
			elif network.product_name or network.product_instance:		# Error
				pass
			elif network.reserved:										# Reserved space.
				reserved_host = network.custom_host or scope_host(to_scope)
				reserved_port = network.custom_port or ANSAR_RESERVED_PORT
				connect_above = ar.HostPort(reserved_host, reserved_port)
			else:														# HostPort for connect_scope -> to_scope
				dedicated_host = network.custom_host or scope_host(to_scope)
				dedicated_port = network.custom_port or ANSAR_DEDICATED_PORT
				connect_above = ar.HostPort(dedicated_host, dedicated_port)

		elif network.connect_scope and network.connect_file:			# Explicit.
			connect_file = network.connect_file
			try:
				f = ar.File(connect_file, ar.Any(), decorate_names=False)
				connect_above, _ = f.recover()
			except (ar.FileFailure, ar.CodecError) as e:
				s = str(e)
				f = ar.Failed(connect_file=(s, None))
				self.complete(f)
			
		elif network.connect_scope and network.connect_disable:			# Explicit.
			connect_above = ar.HostPort()

		elif network.connect_scope or network.to_scope:					# Error.
			e = ar.Faulted('need both ends to make a connection', 'use --connect-scope and --to-scope (or --connect-scope and --connect-file)')
			raise ar.Incomplete(e)

		else:	# Scan.
			s = ar.DirectoryScope(scope=GROUP, connect_above=connect_above,
				started=ar.world_now(),
				connected=None)
			e = ar.NetworkEnquiry(lineage=[s])
			self.send(e, self.directory)

			m = self.select(ar.DirectoryAncestry, ar.Stop)
			if isinstance(m, DirectoryAncestry):
				output_ancestry(self, m, network)
				return None
			return None

		if network.to_scope and network.to_scope <= network.connect_scope:
			e = ar.Faulted('connection is upside down', 'target scope must be higher than the source scope')
			raise ar.Incomplete(e)

		a = ar.NetworkConnect(scope=network.connect_scope, connect_above=connect_above)
		self.send(a, self.directory)

		m = self.select(ar.Anything, ar.Ack, ar.Faulted, ar.Stop)
		if isinstance(m, ar.Anything):		# Group change.
			settings = hr.role_settings[2]
			settings.connect_above = m.thing
			try:
				decoration_store(hr.role_settings, settings)
			except (ar.FileFailure, ar.CodecFailed) as e:
				self.reply(ar.Failed(group_connect=(e, None)))
			self.reply(ar.Ack())
		elif isinstance(m, ar.Ack):			# Didnt involve group change.
			return None
		elif isinstance(m, ar.Faulted):		# Failure in the hierarchy.
			return m
		else:
			return None
		# Now the response to the actual
		# NetworkConnect request.
		m = self.select(ar.Ack, ar.Stop)
		return None

	finally:
		self.send(ar.Stop(), self.directory)
		self.select(ar.Completed, ar.Stop)

	return None
'''
	if self.settings.connect_scope:
		#self.settings.connect_above = message
		self.start(ar.T2, seconds=1.5)
		return RECONNECTING

def Group_RECONNECTING_T2(self, message):
	try:
		f = ar.File(self.settings.connect_file, ar.Any(), decorate_names=False)
		connect_above, _ = f.recover()
	except (ar.FileFailure, ar.CodecError) as e:
		s = str(e)
		f = ar.Failed(connect_file=(s, None))
		self.complete(f)
	a = ar.NetworkConnect(scope=self.settings.connect_scope, connect_above=connect_above)
	self.send(a, self.directory)
	return RECONNECTING

def Group_RECONNECTING_Anything(self, message):
	# The DirectoryConnect sent above has been routed to this
	# directory owner, i.e. the scope was set to GROUP.
	hr = ar.object_role()

	settings = hr.role_settings[2]
	settings.connect_above = message.thing
	try:
		decoration_store(hr.role_settings, settings)
	except (ar.FileFailure, ar.CodecFailed) as e:
		r = ar.Failed(group_reconnect=(e, None))
		self.warning(str(r))
	self.reply(ar.Ack())
	return RECONNECTING

def Group_RECONNECTING_Ack(self, message):
	# This is the Ack sent by the ServiceDirectory after the
	# activity above, i.e. its the final "reply" to the
	# original sending of a NetworkConnect.
	self.complete(message)

	settings = []
	if network.connect_scope:	# Assignment of new connection.
		if not network.connect_file:
			e = ar.Rejected(connect_with_no_file=('missing connection details', None))
			raise ar.Incomplete(e)
		s = ScopeOfService.to_name(network.connect_scope)
		p = os.path.abspath(network.connect_file)
		settings.append(f'--connect-scope={s}')
		settings.append(f'--connect-file={p}')

	else:
		settings.append(f'--show-scopes')

	try:
		a = self.create(ar.Process, 'ansar-group',	
					origin=ar.POINT_OF_ORIGIN.RUN_ORIGIN,
					home_path=hb.home_path, role_name=group_role, subrole=False,
					settings=settings)

		# Wait for Ack from new process to verify that
		# framework is operational.
		m = self.select(ar.Completed, ar.Stop)
		if isinstance(m, ar.Stop):
			# Honor the slim chance of a control-c before
			# the framework can respond.
			self.send(m, a)
			m = self.select(ar.Completed)

		# Process.
		def lfa_text(lfa):
			f, l, a = len(d.listing), len(d.find), len(d.accepted)
			s = f'{f}/{l}/{a}'
			return s

		value = m.value
		if isinstance(value, ar.Ack):	   # New instance established itself.
			pass
		elif isinstance(value, DirectoryAncestry):
			for d in reversed(value.lineage):

				scope = ScopeOfService.to_name(d.scope) if d.scope else '?'
				if isinstance(d.connect_above, ar.HostPort):
					connecting_ipp = d.connect_above
					display_name = str(connecting_ipp)
				elif isinstance(d.connect_above, ProductAccess):
					connecting_ipp = d.connect_above.access_ipp
					e = InstanceOfProduct.to_name(d.connect_above.product_instance)
					display_name = f'{d.connect_above.product_name}/{e}'
				elif isinstance(d.connect_above, WideAreaAccess):
					connecting_ipp = d.connect_above.access_ipp
					display_name = f'{d.connect_above.directory_id}'
				else:
					continue

				if connecting_ipp.host is None:
					continue

				started = ar.world_to_text(d.started) if d.started else '-'
				connected = ar.world_to_text(d.connected) if d.connected else '-'
				lfa = lfa_text(d)

				note = []
				if network.host_and_port:
					note.append(str(connecting_ipp))
				if network.start_time:
					note.append(started)

				if connecting_ipp.host is None:
					note.append('DISABLED')
				elif d.not_connected:
					note.append(d.not_connected)

				key_name = {k: r.search_or_listing for r in d.listing for k in r.route_key}
				if note:
					s = ', '.join(note)
					ar.output_line(f'{scope} {display_name} ({s})')
				else:
					ar.output_line(f'{scope} {display_name}')
				if network.published_services:
					ar.output_line(f'Published services ({len(d.listing)})', tab=1)
					for r in d.listing:
						ar.output_line(f'{r.search_or_listing} ({len(r.route_key)})', tab=2)
				if network.subscribed_searches:
					ar.output_line(f'Subscribed searches ({len(d.find)})', tab=1)
					if network.routed_matches:
						for r in d.find:
							ar.output_line(f'{r.search_or_listing} ({len(r.route_key)})', tab=2)
							for k in r.route_key:
								ar.output_line(f'"{key_name[k]}"', tab=3)
				if network.accepted_processes:
					ar.output_line(f'Accepted processes ({len(d.accepted)})', tab=1)
					for a in d.accepted:
						ar.output_line(f'{a}', tab=2)

		elif isinstance(value, NetworkConnect):
			return value
		elif isinstance(value, ar.Faulted):
			raise ar.Incomplete(value)
		elif isinstance(value, ar.LockedOut):
			e = ar.Failed(role_lock=(None, f'"{group_role}" already running as <{value.pid}>'))
			raise ar.Incomplete(e)
		else:
			e = ar.Failed(role_execute=(value, f'unexpected response from "{group_role}" (ansar-group)'))
			raise ar.Incomplete(e)
	finally:
		pass

	return None
'''

class PingSettings(object):
	def __init__(self, service_name=None, group_name=None, home_path=None, ping_count=None):
		self.service_name = service_name
		self.group_name = group_name
		self.home_path = home_path
		self.ping_count = ping_count

PING_SETTINGS_SCHEMA = {
	'service_name': ar.Unicode(),
	'group_name': ar.Unicode(),
	'home_path': ar.Unicode(),
	'ping_count': ar.Integer8(),
}

ar.bind(PingSettings, object_schema=PING_SETTINGS_SCHEMA)

# Attempt a few pings in the hope there is an echo. A test for connectivity,
# some measure of life-or-death at the remote end and also the time taken
# for a round trip. Which is not representative of the time taken over peer
# connections and relays.
def ping_service(self, service, count):
	p = ar.Ping()
	count = count or 8
	for i in range(count):
		self.send(p, service.agent_address)
		started = ar.clock_now()
		m = self.select(ar.Ack, ar.Stop, seconds=2.0)

		if isinstance(m, ar.Ack):					# An echo.
			span = ar.clock_now() - started
			t = ar.span_to_text(span)
			ar.output_line(f'+ received ack after {t}' )

		elif isinstance(m, ar.SelectTimer):		# Too long.
			ar.output_line('+ timed out')
			continue
		else:
			return	# Interrupted.

		# Insert a delay to allow really slow echoes to
		# pass and to not create a burst of traffic.
		self.start(ar.T1, 1.0)
		m = self.select(ar.T1, ar.Stop)
		if isinstance(m, ar.T1):
			pass
		else:
			return	# Interrupted.

	return ar.Faulted(f'service {service} not found')

# Look for the specified service with the purpose
# of pinging the named agent.
def find_ping(self, lineage, service, count):
	for a in lineage:
		for s in a.listing:
			if s.search_or_listing == service:
				t = ar.ScopeOfService.to_name(a.scope)
				ar.output_line(f'[{t}] {service} ({len(s.agent_address)} hops)')
				ping_service(self, s, count)
				return None

	# No such service.
	return ar.Faulted(f'service {service} not found')

def procedure_ping(self, ping, service, group, home):
	service = ar.word_argument_2(service, ping.service_name, None, 'service')
	group = ar.word_argument_2(group, ping.group_name, DEFAULT_GROUP, GROUP)
	home = ar.word_argument_2(home, ping.home_path, DEFAULT_HOME, HOME)

	if '.' in group:
		e = ar.Rejected(group_name=(group, f'no-dots name'))
		raise ar.Incomplete(e)
	group_role = f'group.{group}'

	hb = open_home(home)

	if not hb.role_exists(group_role):
		e = ar.Failed(group_exists=(f'group "{group}" not found', None))
		raise ar.Incomplete(e)

	_, running = role_status(self, hb, [group_role])
	if running:
		e = ar.Failed(group_running=(f'group "{group}" is already running', None))
		raise ar.Incomplete(e)

	settings = GroupSettings()
	hr = hb.open_role(group_role, settings, None, ar.NodeProperties())

	settings = hr.role_settings[2]				# From the group.
	connect_above = settings.connect_above
	accept_below = ar.LocalPort(0)				# Disabled.

	a = self.create(ar.ServiceDirectory, ar.ScopeOfService.GROUP, connect_above, accept_below)
	self.assign(a, None)
	self.directory = a

	try:
		# Directory responds with a HostPort
		# Then wait for a grace period.
		m = self.select(ar.HostPort, ar.Stop)
		if isinstance(m, ar.HostPort):
			connect_above = m
		self.start(ar.T2, seconds=1.5)
		self.select(ar.T2, ar.Stop)

		s = ar.DirectoryScope(connect_above=connect_above,
			started=ar.world_now(),
			connected=None)
		e = ar.NetworkEnquiry(lineage=[s])
		self.send(e, self.directory)

		m = self.select(ar.DirectoryAncestry, ar.Stop)
		if isinstance(m, DirectoryAncestry):
			return find_ping(self, m.lineage, service, ping.ping_count)

	finally:
		self.send(ar.Stop(), self.directory)
		self.select(ar.Completed, ar.Stop)

	return None

# Keyboard input.
# Form/field filling.
def fill_field(name, t):
	if name == 'password':
		d = getpass.getpass(f'Password: ')
		return d

	ip = name.capitalize()
	ip = ip.replace('_', ' ')
	kb = input(f'{ip}: ')

	if isinstance(t, QUOTED_TYPE):
		sh = SHIPMENT_WITH_QUOTES % (kb,)
	else:
		sh = SHIPMENT_WITHOUT_QUOTES % (kb,)
	try:
		encoding = ar.CodecJson()
		d, _ = encoding.decode(sh, t)
	except ar.CodecFailed as e:
		f = ar.Faulted(f'cannot accept input for "{ip}"', str(e))
		raise ar.Incomplete(f)
	return d

def fill_form(self, form):
	schema = form.__art__.value
	for k, v in schema.items():
		if k == 'login_token':
			continue
		t = getattr(form, k, None)
		if t is not None:
			continue
		d = fill_field(k, v)
		setattr(form, k, d)

#
#
class AccountSettings(object):
	def __init__(self, read=False, update=False, delete=False, add_login=False, add_directory=False,
			organization_name=None, organization_location=None,
			show_identities=False, show_times=False):
		self.read = read
		self.update = update
		self.delete = delete
		self.add_login = add_login
		self.add_directory = add_directory
		self.organization_name = organization_name
		self.organization_location = organization_location
		self.show_identities = show_identities
		self.show_times = show_times

ACCOUNT_SETTINGS_SCHEMA = {
	'read': ar.Boolean(),
	'update': ar.Boolean(),
	'delete': ar.Boolean(),
	'add_login': ar.Boolean(),
	'add_directory': ar.Boolean(),
	'organization_name': ar.Unicode(),
	'organization_location': ar.Unicode(),
	'show_identities': ar.Boolean(),
	'show_times': ar.Boolean(),
}

ar.bind(AccountSettings, object_schema=ACCOUNT_SETTINGS_SCHEMA)

# Standardize checking and diagnostics for all the
# cloud interactions.
def crud_address_and_token(crud, ipp, token):
	if crud > 1:
		f = ar.Faulted('multiple operations specified', 'not supported')
		return f
	if not ipp:
		f = ar.Faulted('no address defined for the ansar cloud', 'use --cloud-ip=<address> --store-settings')
		return f
	if not token:
		f = ar.Faulted('not logged in', 'need to signup or login')
		return f
	return None

# Create a new account.
def procedure_signup(self, account):
	settings = ar.object_custom_settings()
	cloud_ip = settings.cloud_ip

	f = crud_address_and_token(1, cloud_ip, uuid.uuid4())
	if f:
		return f

	ar.connect(self, ar.HostPort(cloud_ip, FOH_PORT))
	m = self.select(ar.Connected, ar.NotConnected, ar.Stop)
	if isinstance(m, ar.Connected):
		session = self.return_address
	elif isinstance(m, ar.NotConnected):
		return m
	else:
		return ar.Aborted()

	try:
		return account_signup(self, session)	# Create account in cloud, clobber token.
	finally:
		self.send(ar.Close(), session)
		self.select(ar.Closed, ar.Stop)

# Refresh the session with an account.
def procedure_login(self, account):
	settings = ar.object_custom_settings()
	cloud_ip = settings.cloud_ip
	login_token = settings.login_token

	f = crud_address_and_token(1, cloud_ip, login_token)
	if f:
		return f

	ar.connect(self, ar.HostPort(cloud_ip, FOH_PORT))
	m = self.select(ar.Connected, ar.NotConnected, ar.Stop)
	if isinstance(m, ar.Connected):
		session = self.return_address
	elif isinstance(m, ar.NotConnected):
		return m
	else:
		return ar.Aborted()

	try:
		self.trace(f'read: {account.read}')
		if account.read:
			return login_read(self, login_token, session, account)
		return account_login(self, session)		# Creds for existing account, update token.
	finally:
		self.send(ar.Close(), session)
		self.select(ar.Closed, ar.Stop)

def login_read(self, login_token, session, account):
	read = LoginRead(login_token=login_token)
	fill_form(self, read)
	self.send(read, session)
	m = self.select(LoginPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, LoginPage):
		output_login(m, account)
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

# CRUD for the account entity. Well, more like RUD as
# the create part is covered by signup and login.
def procedure_account(self, account):
	settings = ar.object_custom_settings()
	cloud_ip = settings.cloud_ip
	login_token = settings.login_token

	crud = sum([account.read, account.update, account.delete, account.add_login, account.add_directory])

	f = crud_address_and_token(crud, cloud_ip, login_token)
	if f:
		return f

	ar.connect(self, ar.HostPort(cloud_ip, FOH_PORT))
	m = self.select(ar.Connected, ar.NotConnected, ar.Stop)
	if isinstance(m, ar.Connected):
		session = self.return_address
	elif isinstance(m, ar.NotConnected):
		return m
	else:
		return ar.Aborted()

	try:
		if account.update:
			return account_update(self, login_token, session, account)
		elif account.delete:
			return account_delete(self, login_token, session)
		elif account.add_login:
			return account_add_login(self, login_token, session)
		elif account.add_directory:
			return account_add_directory(self, login_token, session)
		return account_read(self, login_token, session, account)
	finally:
		self.send(ar.Close(), session)
		self.select(ar.Closed, ar.Stop)

def account_signup(self, session):
	signup = AccountSignup()
	fill_form(self, signup)
	self.send(signup, session)
	m = self.select(AccountOpened, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, AccountOpened):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()

	settings = ar.object_custom_settings()
	settings.login_token = m.login_token
	ar.store_settings(settings)
	return None

def account_login(self, session):
	login = AccountLogin()
	fill_form(self, login)
	self.send(login, session)
	m = self.select(AccountOpened, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, AccountOpened):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()

	settings = ar.object_custom_settings()
	settings.login_token = m.login_token
	ar.store_settings(settings)
	return None

def account_read(self, login_token, session, account):
	read = AccountRead(login_token=login_token)
	self.send(read, session)
	m = self.select(AccountPage, ar.Faulted, ar.Abandoned, ar.Closed, ar.Stop)
	if isinstance(m, AccountPage):
		output_account(m, account)
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, (ar.Abandoned, ar.Closed)):
		f = ar.Faulted('lost remote connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def account_update(self, login_token, session, account):
	update = AccountUpdate(login_token=login_token,
		organization_name=account.organization_name, organization_location=account.organization_location)

	if not account.organization_name and not account.organization_location:
		fill_form(self, update)
	self.send(update, session)
	m = self.select(AccountPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, AccountPage):
		return m
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def account_delete(self, login_token, session):
	delete = AccountDelete(login_token=login_token)
	self.send(delete, session)
	m = self.select(AccountDeleted, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, AccountDeleted):
		return None
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def account_add_login(self, login_token, session):
	add = AccountAddLogin(login_token=login_token)
	fill_form(self, add)
	self.send(add, session)
	m = self.select(LoginPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, LoginPage):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def account_add_directory(self, login_token, session):
	add = AccountAddDirectory(login_token=login_token)
	fill_form(self, add)
	self.send(add, session)
	m = self.select(DirectoryPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, DirectoryPage):
		pass
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

'''		self.account_id = account_id				# Unique key.
		self.organization_name = organization_name
		self.organization_location = organization_location
		self.technical_contact = technical_contact or ar.default_vector()
		self.financial_contact = financial_contact or ar.default_vector()
		self.administrative_contact = administrative_contact or ar.default_vector()
		self.number_of_logins = number_of_logins
		self.number_of_directories = number_of_directories
		self.number_of_relays = number_of_relays
		# Payment
		# Invoices
		self.login_page = login_page or ar.default_vector()
		self.directory_page = directory_page or ar.default_vector()

		self.login_id = login_id			# Unique key.
		self.login_email = login_email
		self.account_id = account_id		# Belong to this account.
		self.assigned_directory = assigned_directory or ar.default_set()	# Assigned use of.
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific

		self.directory_id = directory_id			# Unique key.
		self.product_name = product_name
		self.product_instance = product_instance
		self.number_of_tokens = number_of_tokens
		self.connected_routes = connected_routes
		self.messages_per_second = messages_per_second
		self.bytes_per_second = bytes_per_second
		self.exported_name = exported_name or ar.default_vector()
'''

#
#
class DirectorySettings(object):
	def __init__(self, read=False, update=False, export=False,
			directory_id=None, export_file=None, access_name=None,
			show_identities=False, show_times=False):
		self.read = read
		self.update = update
		self.export = export
		self.directory_id = directory_id
		self.export_file = export_file
		self.access_name = access_name
		self.show_identities = show_identities
		self.show_times = show_times

DIRECTORY_SETTINGS_SCHEMA = {
	'read': ar.Boolean(),
	'update': ar.Boolean(),
	'export': ar.Boolean(),
	'directory_id': ar.UUID(),
	'export_file': ar.Unicode(),
	'access_name': ar.Unicode(),
	'show_identities': ar.Boolean(),
	'show_times': ar.Boolean(),
}

ar.bind(DirectorySettings, object_schema=DIRECTORY_SETTINGS_SCHEMA)

#
#
def procedure_directory(self, directory):
	settings = ar.object_custom_settings()
	cloud_ip = settings.cloud_ip
	login_token = settings.login_token

	crud = sum([directory.read, directory.update, directory.export])

	f = crud_address_and_token(crud, cloud_ip, login_token)
	if f:
		return f

	ar.connect(self, ar.HostPort(cloud_ip, FOH_PORT))
	m = self.select(ar.Connected, ar.NotConnected, ar.Stop)
	if isinstance(m, ar.Connected):
		session = self.return_address
	elif isinstance(m, ar.NotConnected):
		return m
	else:
		return ar.Aborted()

	try:
		if directory.update:
			return directory_update(self, login_token, session, directory)
		elif directory.export:
			return directory_export(self, login_token, session, directory)
		return directory_read(self, login_token, session, directory)
	finally:
		self.send(ar.Close(), session)
		self.select(ar.Closed, ar.Stop)

def directory_read(self, login_token, session, directory):
	read = DirectoryRead(login_token=login_token,
		directory_id=directory.directory_id)
	fill_form(self, read)
	if not directory.directory_id:
		f = ar.Faulted('directory id not specified', 'use --directory-id=<uuid>')
		return f
	self.send(read, session)
	m = self.select(DirectoryPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, DirectoryPage):
		output_directory(m, directory)
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def directory_update(self, login_token, session, directory):
	update = DirectoryUpdate(login_token=login_token, directory_id=directory.directory_id)
	fill_form(self, update)
	if not directory.directory_id:
		f = ar.Faulted('directory id not specified', 'use --directory-id=<uuid>')
		return f
	self.send(update, session)
	m = self.select(DirectoryPage, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, DirectoryPage):
		return m
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def output_access(access, export_file):
	if not export_file:
		try:
			encoding = ar.CodecJson(pretty_format=True)
			s = encoding.encode(access, ar.Any())
		except ar.CodecError as e:
			s = str(e)
			f = ar.Failed(encode_access=(s, None))
			return f
		ar.output_line(s)
		return None

	try:
		f = ar.File(export_file, ar.Any(), decorate_names=False)
		f.store(access)
	except (ar.FileFailure, ar.CodecError) as e:
		s = str(e)
		f = ar.Failed(encode_access_file=(s, None))
		return f
	return None

def directory_export(self, login_token, session, directory):
	settings = ar.object_custom_settings()
	cloud_ip = settings.cloud_ip

	export = DirectoryExport(login_token=login_token,
		directory_id=directory.directory_id, access_name=directory.access_name)
	fill_form(self, export)
	if not export.directory_id:
		f = ar.Faulted('directory id not specified', 'use --directory-id=<uuid>')
		return f
	if not export.access_name:
		f = ar.Faulted('access name not specified', 'use --access-name=<uuid>')
		return f
	self.send(export, session)
	m = self.select(DirectoryExported, ar.Faulted, ar.Abandoned, ar.Stop)
	if isinstance(m, DirectoryExported):
		cloud_ipp = ar.HostPort(cloud_ip, FOH_PORT)
		w = WideAreaAccess(access_ipp=cloud_ipp, access_token=m.access_token,
			account_id=m.account_id, directory_id=m.directory_id,
			product_name=m.product_name, product_instance=m.product_instance)
		f = output_access(w, directory.export_file)
		if f:
			return f
		return None
	elif isinstance(m, ar.Faulted):
		return m
	elif isinstance(m, ar.Abandoned):
		f = ar.Faulted('remote abandoned connection', 'try later?')
		return f
	else:
		return ar.Aborted()
	return None

def output_account(account, settings):
	account_identity = ''

	notes = []
	if settings.show_identities:
		notes.append(f'{account.account_id}')
	if settings.show_times:
		t = ar.world_to_text(account.created)
		notes.append(t)

	if notes:
		n = ', '.join(notes)
		account_identity = f' ({n})'
	ar.output_line(f'+ Account {account}{account_identity}')
	ar.output_line(f'+ Number of logins: {account.number_of_logins}', tab=1)
	ar.output_line(f'+ Number of directores: {account.number_of_directories}', tab=1)
	ar.output_line(f'+ Number of relays: {account.number_of_relays}', tab=1)

	ar.output_line(f'+ Logins ({len(account.login_page)})', tab=1)
	for l in account.login_page:
		login_identity = ''
		login_notes = []
		if settings.show_identities:
			login_notes.append(f'{l.login_id}')
		if settings.show_times:
			t = ar.world_to_text(l.created)
			login_notes.append(t)

		if login_notes:
			n = ', '.join(login_notes)
			login_identity = f' ({n})'
		ar.output_line(f'+ {l}{login_identity}', tab=2)
		ar.output_line(f'+ Login email: {l.login_email}', tab=3)
		ar.output_line(f'+ Family name: {l.family_name}', tab=3)
		ar.output_line(f'+ Given name: {l.given_name}', tab=3)
		ar.output_line(f'+ Nick name: {l.nick_name}', tab=3)
		ar.output_line(f'+ Honorific: {l.honorific}', tab=3)

	ar.output_line(f'+ Directories ({len(account.directory_page)})', tab=1)
	for d in account.directory_page:
		directory_identity = ''
		directory_notes = []
		if settings.show_identities:
			directory_notes.append(f'{d.directory_id}')
		if settings.show_times:
			t = ar.world_to_text(d.created)
			directory_notes.append(t)

		if directory_notes:
			n = ', '.join(directory_notes)
			directory_identity = f' ({n})'
		ar.output_line(f'+ {d}{directory_identity}', tab=2)
		ar.output_line(f'+ Number of tokens: {d.number_of_tokens}', tab=3)
		ar.output_line(f'+ Connected routes: {d.connected_routes}', tab=3)
		ar.output_line(f'+ Messages per second: {d.messages_per_second}', tab=3)
		ar.output_line(f'+ Bytes per second: {d.bytes_per_second}', tab=3)
		ar.output_line(f'+ Exported token ({len(d.exported_name)})', tab=3)
		for t in d.exported_name:
			ar.output_line(f'+ {t}', tab=4)

def output_login(login, settings):
	login_identity = ''

	notes = []
	if settings.show_identities:
		notes.append(f'{login.account_id}')
	if settings.show_times:
		t = ar.world_to_text(login.created)
		notes.append(t)

	if notes:
		n = ', '.join(notes)
		login_identity = f' ({n})'

	ar.output_line(f'+ {login}{login_identity}')
	ar.output_line(f'+ Login email: {login.login_email}', tab=1)
	ar.output_line(f'+ Family name: {login.family_name}', tab=1)
	ar.output_line(f'+ Given name: {login.given_name}', tab=1)
	ar.output_line(f'+ Nick name: {login.nick_name}', tab=1)
	ar.output_line(f'+ Honorific: {login.honorific}', tab=1)

def output_directory(directory, settings):
	directory_identity = ''

	notes = []
	if settings.show_identities:
		notes.append(f'{directory.directory_id}')
	if settings.show_times:
		t = ar.world_to_text(directory.created)
		notes.append(t)

	if notes:
		n = ', '.join(notes)
		directory_identity = f' ({n})'

	ar.output_line(f'+ {directory}{directory_identity}')
	ar.output_line(f'+ Number of tokens: {directory.number_of_tokens}', tab=1)
	ar.output_line(f'+ Connected routes: {directory.connected_routes}', tab=1)
	ar.output_line(f'+ Messages per second: {directory.messages_per_second}', tab=1)
	ar.output_line(f'+ Bytes per second: {directory.bytes_per_second}', tab=1)
	ar.output_line(f'+ Exported token ({len(directory.exported_name)})', tab=1)
	for t in directory.exported_name:
		ar.output_line(f'+ {t}', tab=2)
