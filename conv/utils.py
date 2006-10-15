# pydvi2svg
# -*- coding: iso-8859-2 -*-
#
# Some utils
# $Id: utils.py,v 1.2 2006-10-15 16:17:59 wojtek Exp $
# 
# license: BSD
#
# author: Wojciech Mu�a
# e-mail: wojciech_mula@poczta.onet.pl

__changelog__ = '''
15.10.2006
	- funtions parse_pagedef, parse_enc_repl moved from dvi2svg.py
	- added parse_enc_methods
13.10.2006
	- added group_elements
'''

def group_elements(seq, value=lambda x: x):
	"""
	Groups adjecent elements that has some value.
	Groups is a pair: common value, list of elements.
	"""
	if not seq:
		return []

	result = []
	prev   = value(seq[0])
	curr   = prev
	group  = [seq[0]]

	for i in xrange(1, len(seq)):
		curr = value(seq[i])
		if curr == prev:
			group.append(seq[i])
		else:
			result.append( (prev, group) )
			group = [seq[i]]
			prev  = curr
	
	if group:
		result.append( (curr, group) )
	
	return result


def parse_pagedef(string, min, max):
	"""
	Parse page numbers. Examples:
		1,2,5,10	- selected single pages
		2-5		- range (2,5)
		-10		- range (min,10)
		15-		- range (15,max)

	>>> parse_pagedef("1,2,3,4,5", 1, 10)
	[1, 2, 3, 4, 5]
	>>> parse_pagedef("1,-5,2-7",  1, 10)
	[1, 2, 3, 4, 5, 6, 7]
	>>> parse_pagedef("1,5-,3-,2", 1, 10)
	[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	"""
	assert min <= max
	def touint(string):
		try:
			x = int(string)
		except ValueError:
			raise ValueError("Number expeced, got %s" % string)

		if   x < min:
			raise ValueError("Number %d less then %d" % (x, min))
		elif x > max:
			raise ValueError("Number %d greater then %d" % (x, max))
		else:
			return x

	result = []
	for item in string.split(','):
		tmp = item.split('-')
		if   len(tmp) == 1:	# single page (number)
			result.append(touint(tmp[0]))
		elif len(tmp) == 2:	
			# open range (number-)
			if   tmp[0] == '':
				a = min
				b = touint(tmp[1])

			# open range (number-)
			elif tmp[1] == '':
				a = touint(tmp[0])
				b = max

			# range (number-number)
			else:              
				a = touint(tmp[0])
				b = touint(tmp[1])

			result.extend( range(a,b+1) )
		else:
			raise ValueError("Wrong syntax: %s" % item)
	#rof
	return list(Set(result))


def parse_enc_repl(string):
	# format:
	#  fontname:enc,fontname:enc,fontname=enc

	string = string.replace(':', '=')
	dict   = {}
	for item in string.split(','):
		try:
			fontname, enc = item.split('=')
			dict[fontname] = enc
		except ValueError:
			pass
	
	return dict


def parse_enc_methods(list):
	"""
	Format: Cache|C,TFM|T,AMF|A,MAP|M,GUESS|G|E
	Output: ordered set of ['c', 't', 'a', 'm', g']
	"""
	commands = ""
	for method in list.split(","):
		method = method.lower()
		if   method in ['cache', 'c']: method = 'c'
		elif method in ['tfm',   't']: method = 't'
		elif method in ['afm',   'a']: method = 'a'
		elif method in ['map',   'm']: method = 'm'
		elif method in ['guess', 'g', 'e']: method = 'g'
		else:
			# skip unknown methods, do not bother
			# user by raising exception
			continue

		if method not in commands:
			commands += method
	
	return commands


# vim: ts=4 sw=4
