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

"""Definition of messages for client and cloud interactions.

The protocol messages that establish wide-area transports between
pub-sub pairs. Needed here for the ansar CLI and the runtime
handshaking.
"""
__docformat__ = 'restructuredtext'

import ansar.create as ar
from .socketry import *
from .product import *

__all__ = [
	'CONTACT_TYPE',			# Too general to leave in cloud.
	'CONTACT_DEVICE',
	'EmailAddress',
	'PhoneNumber',
	'WideAreaAccess',		# Node to WAN directory.
	'WideAreaLookup',
	'WideAreaRedirect',
	'WideAreaAssignment',
	'YourWideArea',
	'RelayLookup',			# Node to WAN relay.
	'RelayRedirect',
	'RelayAssignment',
	'YourRelay',
	'CloseRelay',
]

# Contact details.
CONTACT_TYPE = ar.Enumeration(PERSONAL=0, BUSINESS=1, HOME=2, OTHER=3)
CONTACT_DEVICE = ar.Enumeration(MOBILE=0, FIXED_LINE=1)

class EmailAddress(object):
	def __init__(self, email_type=None, email_address=None):
		self.email_type = email_type
		self.email_address = email_address

	def __str__(self):
		s = CONTACT_TYPE.to_name(self.email_type)
		return f'[{s}] {self.email_address}'

class PhoneNumber(object):
	def __init__(self, phone_type=None, phone_device=None, phone_number=None):
		self.phone_type = phone_type
		self.phone_device = phone_device
		self.phone_number = phone_number

	def __str__(self):
		t = CONTACT_TYPE.to_name(self.phone_type)
		d = CONTACT_DEVICE.to_name(self.phone_device)
		return f'[{t}/{d}] {self.phone_number}'

#
#
CONTACT_SCHEMA = {
	"email_type": CONTACT_TYPE,
	"email_address": ar.Unicode(),
	"phone_type": CONTACT_TYPE,
	"phone_device": CONTACT_DEVICE,
	"phone_number": ar.Unicode(),
}

ar.bind(EmailAddress, object_schema=CONTACT_SCHEMA)
ar.bind(PhoneNumber, object_schema=CONTACT_SCHEMA)

# Protocol between a connecting directory and
# a cloud directory.
class WideAreaAccess(object):
	def __init__(self, access_ipp=None, access_token=None, account_id=None, directory_id=None,
			product_name=None, product_instance=None):
		self.access_ipp = access_ipp or HostPort()	# Manifestly required.
		self.access_token = access_token
		self.account_id = account_id				# Speed up processing.
		self.directory_id = directory_id
		self.product_name = product_name
		self.product_instance = product_instance

	def __str__(self):
		t = InstanceOfProduct.to_name(self.product_instance)
		return f'{self.product_name}/{t}'

class WideAreaLookup(object):
	def __init__(self, account_id=None, directory_id=None):
		self.account_id = account_id
		self.directory_id = directory_id

class WideAreaRedirect(object):
	def __init__(self, redirect_ipp=None, directory_id=None, assignment_token=None):
		self.redirect_ipp = redirect_ipp or HostPort()
		self.directory_id = directory_id
		self.assignment_token = assignment_token

class WideAreaAssignment(object):
	def __init__(self, directory_id=None, assignment_token=None):
		self.directory_id = directory_id
		self.assignment_token = assignment_token

class YourWideArea(object):
	def __init__(self, address=None):
		self.address = address

WIDE_AREA_SCHEMA = {
	"access_ipp": ar.UserDefined(HostPort),
	"access_token": ar.UUID(),
	"account_id": ar.UUID(),
	"directory_id": ar.UUID(),
	"redirect_ipp": ar.UserDefined(HostPort),
	"assignment_token": ar.UUID(),
	"address": ar.Address(),
	"product_name": ar.Unicode(),
	"product_instance": InstanceOfProduct,
}

ar.bind(WideAreaAccess, object_schema=WIDE_AREA_SCHEMA)
ar.bind(WideAreaLookup, object_schema=WIDE_AREA_SCHEMA)
ar.bind(WideAreaRedirect, object_schema=WIDE_AREA_SCHEMA)
ar.bind(WideAreaAssignment, object_schema=WIDE_AREA_SCHEMA)
ar.bind(YourWideArea, object_schema=WIDE_AREA_SCHEMA)

# Protocol between a routing/looping subscriber and
# a publisher.
class RelayLookup(object):
	def __init__(self, relay_id=None, directory_id=None):
		self.relay_id = relay_id
		self.directory_id = directory_id

class RelayRedirect(object):
	def __init__(self, redirect_ipp=None, relay_id=None, assignment_token=None):
		self.redirect_ipp = redirect_ipp or HostPort()
		self.relay_id = relay_id
		self.assignment_token = assignment_token

class RelayAssignment(object):
	def __init__(self, relay_id=None, assignment_token=None):
		self.relay_id = relay_id
		self.assignment_token = assignment_token

class YourRelay(object):
	def __init__(self, address=None):
		self.address = address

class CloseRelay(object):
	def __init__(self, redirect=None):
		self.redirect = redirect or RelayRedirect()

RELAY_SCHEMA = {
	"relay_id": ar.UUID(),
	"directory_id": ar.UUID(),
	"redirect_ipp": ar.UserDefined(HostPort),
	"assignment_token": ar.UUID(),
	"address": ar.Address(),
	"account_id": ar.UUID(),
}

ar.bind(RelayLookup, object_schema=RELAY_SCHEMA)
ar.bind(RelayRedirect, object_schema=RELAY_SCHEMA)
ar.bind(RelayAssignment, object_schema=RELAY_SCHEMA)
ar.bind(YourRelay, object_schema=RELAY_SCHEMA)

#
#
class CloseRelay(object):
	def __init__(self, redirect=None):
		self.redirect = redirect or RelayRedirect()

CLOSE_SCHEMA = {
	"redirect": ar.UserDefined(RelayRedirect),
}

ar.bind(CloseRelay, object_schema=CLOSE_SCHEMA)
