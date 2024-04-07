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
'''Interface for the cloud. Needed for ansar CLI.

Defined here so that dependency is from cloud to ansar-connect, rather
than linking ansar-connect to the cloud. Cloud codebase not dragged into
this library.
'''

import ansar.connect as ar
from ansar.connect.product import *

__all__ = [
	'FOH_PORT',
	'AccountSignup',
	'AccountLogin',
	'AccountRead',
	'AccountUpdate',
	'AccountDelete',
	'AccountAddLogin',
	'AccountAddDirectory',
	'LoginRead',
	'DirectoryRead',
	'DirectoryUpdate',
	'DirectoryExport',
	'AccountOpened',
	'DirectoryExported',
	'DirectoryPage',
	'AccountPage',
	'LoginPage',
	'LoginDeleted',
	'AccountDeleted',
	'DirectoryDeleted',
]

FOH_PORT=5022

# Forms to present to the cloud foh.
# Open an existing session with an account/developer
class AccountSignup(object):
	def __init__(self, login_email=None, password=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			organization_name=None, organization_location=None):
		self.login_email = login_email
		self.password = password
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific
		self.organization_name = organization_name
		self.organization_location = organization_location

class AccountLogin(object):
	def __init__(self, login_email=None, password=None):
		self.login_email = login_email
		self.password = password

class AccountRead(object):
	def __init__(self, login_token=None):
		self.login_token = login_token

class AccountUpdate(object):
	def __init__(self, login_token=None, organization_name=None, organization_location=None):
		self.login_token = login_token
		self.organization_name = organization_name
		self.organization_location = organization_location

class AccountDelete(object):
	def __init__(self, login_token=None):
		self.login_token = login_token

class AccountAddLogin(object):
	def __init__(self, login_token=None, login_email=None, password=None,
			family_name=None, given_name=None, nick_name=None, honorific=None):
		self.login_token = login_token
		self.login_email = login_email
		self.password = password
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific

class AccountAddDirectory(object):
	def __init__(self, login_token=None,
			product_name=None, product_instance=None):
		self.login_token = login_token
		self.product_name = product_name
		self.product_instance = product_instance

class LoginRead(object):
	def __init__(self, login_token=None):
		self.login_token = login_token

class DirectoryRead(object):
	def __init__(self, login_token=None, directory_id=None):
		self.login_token = login_token
		self.directory_id = directory_id

class DirectoryUpdate(object):
	def __init__(self, login_token=None, directory_id=None):
		self.login_token = login_token
		self.directory_id = directory_id

class DirectoryExport(object):
	def __init__(self, login_token=None, directory_id=None, access_name=None):
		self.login_token = login_token
		self.directory_id = directory_id
		self.access_name = access_name

SHARED_SCHEMA = {
	"login_token": ar.UUID(),
	"login_email": ar.Unicode(),
	"password": ar.Unicode(),
	"family_name": ar.Unicode(),
	"given_name": ar.Unicode(),
	"nick_name": ar.Unicode(),
	"honorific": ar.Unicode(),
	"organization_name": ar.Unicode(),
	"organization_location": ar.Unicode(),
	"account_id": ar.UUID(),
	"product_name": ar.Unicode(),
	"product_instance": InstanceOfProduct,
	"directory_id": ar.UUID(),
	"exported_access": ar.VectorOf(ar.Unicode()),
	"number_of_logins": ar.Integer8(),
	"number_of_directories": ar.Integer8(),
	"number_of_relays": ar.Integer8(),
	"number_of_tokens": ar.Integer8(),
	"connected_routes": ar.Integer8(),
	"messages_per_second": ar.Integer8(),
	"bytes_per_second": ar.Integer8(),
	"exported_name": ar.VectorOf(ar.Unicode()),
	"directory_id": ar.UUID(),
	"account_id": ar.UUID(),
	"technical_contact": ar.VectorOf(ar.Any()),
	"financial_contact": ar.VectorOf(ar.Any()),
	"administrative_contact": ar.VectorOf(ar.Any()),
	"login_id": ar.UUID(),
	"assigned_directory": ar.SetOf(ar.UUID()),
	"access_token": ar.UUID(),
	"access_name": ar.Unicode(),
	"created": ar.WorldTime(),
}

ar.bind(AccountSignup, object_schema=SHARED_SCHEMA)
ar.bind(AccountLogin, object_schema=SHARED_SCHEMA)
ar.bind(AccountRead, object_schema=SHARED_SCHEMA)
ar.bind(AccountUpdate, object_schema=SHARED_SCHEMA)
ar.bind(AccountDelete, object_schema=SHARED_SCHEMA)
ar.bind(AccountAddLogin, object_schema=SHARED_SCHEMA)
ar.bind(AccountAddDirectory, object_schema=SHARED_SCHEMA)
ar.bind(LoginRead, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryRead, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryUpdate, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryExport, object_schema=SHARED_SCHEMA)

# Forms and responses to present to cloud clients.
class AccountOpened(object):
	def __init__(self, login_token=None):
		self.login_token = login_token

# Read/update response covered by AccountPage.

class LoginDeleted(object): pass
class AccountDeleted(object): pass
class DirectoryDeleted(object): pass

class DirectoryExported(object):
	def __init__(self, directory_id=None, access_token=None, account_id=None,
			product_name=None, product_instance=None):
		self.directory_id = directory_id
		self.access_token = access_token
		self.account_id = account_id
		self.product_name = product_name
		self.product_instance = product_instance

class DirectoryPage(object):
	def __init__(self, directory_id=None, product_name=None, product_instance=None,
			number_of_tokens=None, connected_routes=None, messages_per_second=None, bytes_per_second=None,
			exported_name=None, created=None):
		self.directory_id = directory_id			# Unique key.
		self.product_name = product_name
		self.product_instance = product_instance
		self.number_of_tokens = number_of_tokens
		self.connected_routes = connected_routes
		self.messages_per_second = messages_per_second
		self.bytes_per_second = bytes_per_second
		self.exported_name = exported_name or ar.default_vector()
		self.created = created

	def __str__(self):
		s = InstanceOfProduct.to_name(self.product_instance)
		return f'{self.product_name}/{s}'

class AccountPage(object):
	def __init__(self, account_id=None,
			organization_name=None, organization_location=None, technical_contact=None, financial_contact=None, administrative_contact=None,
			number_of_logins=None, number_of_directories=None, number_of_relays=None, created=None,
			login_page=None, directory_page=None):
		self.account_id = account_id				# Unique key.
		self.organization_name = organization_name
		self.organization_location = organization_location
		self.technical_contact = technical_contact or ar.default_vector()
		self.financial_contact = financial_contact or ar.default_vector()
		self.administrative_contact = administrative_contact or ar.default_vector()
		self.number_of_logins = number_of_logins
		self.number_of_directories = number_of_directories
		self.number_of_relays = number_of_relays
		self.created = created
		# Payment
		# Invoices
		self.login_page = login_page or ar.default_vector()
		self.directory_page = directory_page or ar.default_vector()

	def __str__(self):
		return f'{self.organization_name}'

class LoginPage(object):
	def __init__(self, login_id=None, login_email=None,
			account_id=None, assigned_directory=None,
			family_name=None, given_name=None, nick_name=None, honorific=None,
			created=None):
		self.login_id = login_id			# Unique key.
		self.login_email = login_email
		self.account_id = account_id		# Belong to this account.
		self.assigned_directory = assigned_directory or ar.default_set()	# Assigned use of.
		self.family_name = family_name
		self.given_name = given_name
		self.nick_name = nick_name
		self.honorific = honorific
		self.created = created

	def __str__(self):
		if self.nick_name:
			return self.nick_name

		if self.honorific:
			h = f'{self.honorific} '
		else:
			h = ''

		if self.family_name:
			if self.given_name:
				return f'{h}{self.given_name} {self.family_name}'
			return f'{h}{self.family_name}'
		elif self.given_name:
				return self.given_name

		return self.login_email

ar.bind(AccountOpened, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryExported, object_schema=SHARED_SCHEMA)
ar.bind(LoginPage, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryPage, object_schema=SHARED_SCHEMA)

DIRECTORY_SCHEMA = {
	"login_page": ar.VectorOf(ar.UserDefined(LoginPage)),
	"directory_page": ar.VectorOf(ar.UserDefined(DirectoryPage)),
}
DIRECTORY_SCHEMA.update(SHARED_SCHEMA)

ar.bind(AccountPage, object_schema=DIRECTORY_SCHEMA)
ar.bind(LoginDeleted, object_schema=SHARED_SCHEMA)
ar.bind(AccountDeleted, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryDeleted, object_schema=SHARED_SCHEMA)
ar.bind(DirectoryDeleted, object_schema=SHARED_SCHEMA)
