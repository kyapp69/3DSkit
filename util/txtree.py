# -*- coding:utf-8 -*-
from collections import OrderedDict


def hexformat(n, align):
	align = str(align)
	return ('0x%0' + align + 'x') % n


class ClsFunc(object):
	'''A class which emulates a function. Useful to split big functions into small modules which share data'''
	def __new__(cls, *args, **kwargs):
		ins = object.__new__(cls)
		return ins.main(*args, **kwargs)


class dump (ClsFunc):
	def main(self, tree, customs=[]):
		self.customs = customs
		return self.dumpNode(tree)
	
	def dumpNode(self, node):
		final = ''
		for key in node.keys():
			if key.__class__ == str:
				if key.startswith('__'):
					continue
			if node[key].__class__ in [dict, OrderedDict] + self.customs:
				blk = self.dumpNode(node[key])
				blk = self.indent(blk)
				final += '%s: \n' % key
				final += blk
			elif node[key].__class__ in (list, tuple):
				dic = dict(enumerate(node[key]))
				blk = self.dumpNode(dic)
				blk = self.indent(blk)
				if node[key].__class__ == list:
					final += '[%s]: \n' % key
				elif node[key].__class__ == tuple:
					final += '(%s): \n' % key
				final += blk
			elif node[key].__class__ == str:
				if len(node[key]) >= 1:
					if node[key][0].isdigit():
						node[key] = '"' + node[key].replace('"', '\\"') + '"'
				final += '%s: %s\n' % (key, node[key].replace('\n', '\\n'))
			else:
				final += '%s: %s\n' % (key, repr(node[key]).replace('\n', '\\n'))
		return final
	
	def indent(self, s):
		ret = ''
		for line in s.splitlines():
			ret += '	|%s\n' % line
		return ret


class load (ClsFunc):
	def main(self, data):
		return self.loadNode(data)
	
	def loadNode(self, node):
		dic = OrderedDict()
		node = node.splitlines()
		i = 0
		while True:
			try:
				line = node[i].split(': ')
				if len(line) == 1:
					line.append('')
			except IndexError:
				break
			if not line[0].isdigit() and not line[0].startswith(('b"', "b'")):
				key = line[0]
			else:
				key = eval(line[0])
			if line[1].strip() == '':
				subnode = ''
				for subline in node[i + 1:]:
					if subline.startswith('\t|'):
						subnode += subline + '\n'
						i += 1
					else:
						break
				res = self.loadNode(self.unindent(subnode))
				if line[0].startswith('[') and line[0].endswith(']'):
					res = list(res.values())
				elif line[0].startswith('(') and line[0].endswith(')'):
					res = tuple(res.values())
				elif len(res) == 0:
					res = ''
				dic[line[0].strip('[]()')] = res
			else:
				if line[1].lower() in ('true', 'false', 'none'):
					res = eval(line[1].capitalize())
				elif not line[1].strip('-+')[0].isdigit() and not line[1].startswith(('b"', "b'")):
					if line[1].strip('"')[0].isdigit() and line[1].startswith('"') and line[1].endswith('"'):
						res = line[1][1:-1].replace('\\n', '\n').replace('\\"', '"')
					else:
						res = line[1].replace('\\n', '\n')
				else:
					res = eval(line[1])
				dic[key] = res
			i += 1
		return dic
	
	def unindent(self, s):
		s = s.splitlines()
		ret = ''
		for line in s:
			ret += '%s\n' % line[2:]
		return ret
