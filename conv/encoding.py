# pydvi2svg
# -*- coding: iso-8859-2 -*-
#
# Encoding and ENC file support
# $Id: encoding.py,v 1.3 2006-10-08 21:27:23 wojtek Exp $
# 
# license: BSD
#
# author: Wojciech Mu�a
# e-mail: wojciech_mula@poczta.onet.pl

__changelog__ = '''
  4.10.2006
	- ENCFileError, EncodingDB
  3.10.2006
	- read_ENC
'''

import os
import findfile

class EncodingDBError(Exception):
	pass

class EncodingDB:
	def __init__(self, search_path, tex_search_paths=[]):
		self.search_path		= search_path
		self.tex_search_paths	= tex_search_paths

		self.lastused	= None
		self.loaded_enc	= {}
	
	def getencodingtbl(self, encodingname):
		try:
			return self.loaded_enc[encodingname]
		except KeyError:
			return self.load_encoding(encodingname)
	
	def getcharname(self, encodingname, dvicharcode):
		"""
		Returns character name of char code using given encoding

		For example if encodingname=='cork' (old TeX encoding)
		and dvicharcode==0x10, then returned name have to be 'quotedblleft'.
		"""

		# last used encoding used once again - "cache hit"
		if encodingname == self.lastused:
			return self.lastused[dvicharcode]

		# "cache miss"
		else:
			# ok, encoding already loaded, use it
			if encodingname not in self.loaded_enc:
				self.lastused = self.loaded_enc[encodingname]
				return self.lastused[dvicharcode]

			# encoding not loaded, try to find .enc file, and load
			else:
				self.lastused = self.load_encoding(encodingname)
				return self.lastused[dvicharcode]

	def load_encoding(self, encodingname):
		"""Loads encoding"""

		# try to load encoding from our base directory
		filename = os.path.join(self.search_path, encodingname + ".enc")
		if os.path.exists(filename):
			self.loaded_enc[encodingname] = read_ENC( open(filename, 'r') )[1]
			return self.loaded_enc[encodingname]
		
		# locate encoding in the user filestystem
		filename = findfile.locate(encodingname + ".enc")
		if filename:
			self.loaded_enc[encodingname] = read_ENC( open(filename, 'r') )[1]
			return self.loaded_enc[encodingname]
		else:
			raise EncodingDBError("Can not find '%s.enc' file." % encodingname)



class ENCFileError(Exception):
	def __init__(self, filename, strerror):
		Exception.__init__()
		self.filename	= filename
		self.strerror	= strerror
	
	def __str__(self):
		return self.filename + ": " + self.strerror

def read_ENC(file):
	"""
	Function reads Type1 encoding file, and returns:
	* encoding name
	* character width table
	"""
	def stripcomment(string):
		i = string.find('%')
		if i > -1:
			return string[:i]
		else:
			return string

	# load file, remove comments, put the whole content in a single line
	tmp = ' '.join(stripcomment(line) for line in file.readlines())

	# expeced format:
	# /EncodingName [ /defs_256-times ] def
	#
	obp  = tmp.find('[')
	cbp  = tmp.find(']')
	if not (obp > -1 and cbp > -1):
		raise ENCFileError("Not an ENC file -- braces missing", file.name)

	# get name
	encodingname = tmp[:obp].strip()
	if not (encodingname[0] == '/'):
		raise ENCFileError("Encoding name have to start with '/'", file.name)
	else:
		encodingname = encodingname[1:]

	# check if string ends with string 'def'
	defstr = tmp[cbp+1:].strip()
	if not (defstr == 'def'):
		raise ENCFileError("List of must end with string 'def', but is '%s'" % defstr, file.name)

	# get characters
	name_list = tmp[obp+1:cbp].split()
	if not (len(name_list) == 256):
		raise ENCFileError("File must contain 256 glyphs names", file.name)

	# check their names & fill lookup table
	def get_charname(charname):
		if not (charname[0] == '/'):
			raise ENCFileError("Invalid character name '%s' - it have to start with '/'")
		if charname == '/.notdef':
			return None
		else:
			return charname[1:]

	name_list = [get_charname(name) for name in name_list]

	return encodingname, name_list

# vim: ts=4 sw=4
