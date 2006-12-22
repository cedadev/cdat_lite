# -*- Mode: Python; tab-width: 4 -*-
#
#	Author: Sam Rushing <rushing@nightmare.com>
#	Copyright 1996, 1997 by Sam Rushing
#						 All Rights Reserved.
#
# This software is provided free for non-commercial use.  If you are
# interested in using this software in a commercial context, or in
# purchasing support, please contact the author.

RCS_ID =  '$Id$'

# support for `~user/public_html'.

import regex
import string
import default_handler
import filesys
import os
import pwd

split_path = default_handler.split_path
get_header = default_handler.get_header

user_dir = regex.compile ('/~\([^/]+\)\(.*\)')

class unix_user_handler (default_handler.default_handler):

	def __init__ (self, public_html = 'public_html'):
		self.public_html = public_html
		default_handler.default_handler.__init__ (self, None)

	# cache userdir-filesystem objects
	fs_cache = {}

	def match (self, request):
		if user_dir.match (request.uri) == len(request.uri):
			return 1
		else:
			return 0
			
	def handle_request (self, request):
		# get the user name
		user = user_dir.group(1)
		rest = user_dir.group(2)

		# special hack to catch those lazy URL typers
		if not rest:
			request['Location'] = 'http://%s/~%s/' % (
				request.channel.server.server_name,
				user
				)
			request.error (301)
			return 

		# have we already built a userdir fs for this user?
		if self.fs_cache.has_key (user):
			fs = self.fs_cache[user]
		else:
			# no, well then, let's build one.
			# first, find out where the user directory is
			try:
				info = pwd.getpwnam (user)
			except KeyError:
				request.error (404)
				return
			ud = info[5] + '/' + self.public_html
			if os.path.isdir (ud):
				fs = filesys.os_filesystem (ud)
				self.fs_cache[user] = fs
			else:
				request.error (404)
				return

		# fake out default_handler
		self.filesystem = fs
		# massage the request URI
		request.uri = '/' + rest
		return default_handler.default_handler.handle_request (self, request)

	def __repr__ (self):
		return '<Unix User Directory Handler at %08x [~user/%s, %d filesystems loaded]>' % (
			id(self),
			self.public_html,
			len(self.fs_cache)
			)
