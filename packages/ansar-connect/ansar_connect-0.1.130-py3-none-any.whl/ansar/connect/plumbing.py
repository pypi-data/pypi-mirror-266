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

__all__ = [
	'RETRY_LOCAL',
	'RETRY_PRIVATE',
	'RETRY_PUBLIC',
	'ip_retry',
]

# Reasonable intervals between connection attempts for
# the different scopes of address.
RETRY_LOCAL = ar.RetryIntervals(first_steps=[2.0, 4.0], regular_steps=8.0, step_limit=None, randomized=0.25, truncated=0.5)
RETRY_PRIVATE = ar.RetryIntervals(first_steps=[4.0, 8.0], regular_steps=16.0, step_limit=None, randomized=0.25, truncated=0.5)
RETRY_PUBLIC = ar.RetryIntervals(first_steps=[8.0, 16.0, 32.0], regular_steps=64.0, step_limit=None, randomized=0.25, truncated=0.5)

def ip_retry(s):
	if s == ScopeOfIP.OTHER:	# Not a dotted IP.
		return RETRY_PUBLIC

	if s == ScopeOfIP.LOCAL:		# Local - 127.
		return RETRY_LOCAL
	elif s == ScopeOfIP.PRIVATE:	# Private - 192.168.
		return RETRY_PRIVATE

	return RETRY_PUBLIC				# Domains?
