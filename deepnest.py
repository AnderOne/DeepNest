import re

#Итератор для обхода в глубину сильно вложенных объектов:
class DeepIterator:

	class Pair:
		def __init__(self, key, val):  self.key, self.val = key, val
		def __str__(self): return str((self.key, self.val))

	def __init__(self, obj): self.top, self.obj = [[(obj,), 0]], None

	def __next__(self):

		while self.top and self.top[-1][1] >= len(self.top[-1][0]):
			self.top.pop()

		if not self.top:
			raise StopIteration()

		buf = self.top[-1]
		if len(buf) == 3:
			key = buf[2][buf[1]]; obj = buf[0][key]
			self.obj = DeepIterator.Pair(key, obj)
		else:
			pos = buf[1]; obj = buf[0][pos]
			self.obj = obj
		buf[1] += 1

		if   type(obj) in (frozenset, set, dict):
			self.top.append(
			[obj, 0, sorted(obj.keys())]
			)
		elif type(obj) in (tuple, list):
			self.top.append([obj, 0])
		else:
			self.top.append([[], 0])
		return self.obj

	def __iter__(self):
		return self

	def level(self):
		return len(self.top) - 1

#Обертка для сильно вложенных объектов:
class DeepWrapper:

	def __init__(self, obj): self.obj = obj

	def __eq__(self, rhs):

		if type(rhs) is not DeepWrapper:
			raise TypeError()

		it1 = DeepIterator(self.obj); it2 = DeepIterator(rhs.obj)
		for d1, d2 in zip(it1, it2):
			if it1.level() != it2.level(): return False
			if type(d1) is not type(d2): return False
			if type(d1) is DeepIterator.Pair:
				if d1.key != d2.key:
					return False
				vl = d1.val; vr = d2.val
				if type(vl) is not type(vr):
					return False
				d1 = vl; d2 = vr
			if type(d1) in (
			str, float, int, bool, None
			):
				if d1 != d2:
					return False

		try: next(it1)
		except StopIteration: e1 = True
		else: e1 = False
		try: next(it2)
		except StopIteration: e2 = True
		else: e2 = False

		return e1 and e2

	def items(self):
		return DeepIterator(self.obj)

def dumps(dat):

	dat = DeepIterator(dat); ans = ''; top = []; l = None
	for i in dat:
		while l and l > dat.level():
			ans += top.pop()
			l -= 1
		if l == dat.level():
			ans += ', '
		l = dat.level()
		#Упаковка ассоциативных массивов:
		if type(i) is DeepIterator.Pair:
			ans += '"' + str(i.key) + '": '
			i = i.val
		if type(i) is dict:
			top.append('}')
			ans += '{'
		#Упаковка списков и кортежей:
		if type(i) in (list, tuple):
			top.append(']')
			ans += '['
		#Упаковка скалярных типов:
		if type(i) is bool:
			ans += 'true' if i else 'false'
		if type(i) is str:
			ans += '"' + str(i) + '"'
		if type(i) in (float, int):
			ans += str(i)
		if i is None:
			ans += 'null'
	while top:
		ans += top[-1]
		top.pop()

	return ans

IND_DATA = 1
EXP_BOOL = r'(true|false)'
IND_BOOL = 2
EXP_NULL = r'(null)'
IND_NULL = 3
EXP_NUM = r'([+-]?\d+((\.\d*)?([eE][+-]\d+)?))'
IND_NUM = 4
IND_NUM_FRAC = 5
IND_NUM_DOT = 6
IND_NUM_EXP = 7
EXP_STR = r'("((\\.|[^\\"])*)")'
IND_STR = 8
IND_STR_CHAR = 9
EXP_COL = r'(:)?'
IND_COL = 11
EXP_COM = r'(,)'
IND_COM = 12
EXP_BRC = r'(\[|\]|\{|\})'
IND_BRC = 13

EXP = re.compile(
r'\s*(' + EXP_BOOL + '|' + EXP_NULL + '|' + EXP_NUM + '|' + EXP_STR + r')\s*' + EXP_COL + r'\s*' +\
'|' +\
r'\s*'  + EXP_COM + r'\s*' +\
'|' +\
r'\s*'  + EXP_BRC + r'\s*'
)

def loads(txt):

	if type(txt) is not str: raise TypeError('The JSON object must be str')

	if len(txt) == 0: raise Exception('Unexpected end of string in pos 0')

	top = []; pos = 0; dat = None; fst = True; m = None

	while True:
		if m is not None: pos = m.end()
		if pos >= len(txt): break

		m = EXP.match(txt, pos)
		if m is None: raise Exception('Incorrect syntax in pos ' + str(pos))

		#Проверяем скобки:
		if   m.group(IND_BRC) == '}':
			if not top or type(top[-1][0]) is not dict:
				raise Exception(
				'Extra closing bracket in pos ' + str(pos)
				)
			dat = top[-1][0]
			top.pop()
			fst = False

		elif m.group(IND_BRC) == ']':
			if not top or type(top[-1][0]) is not list:
				raise Exception(
				'Extra closing bracket in pos ' + str(pos)
				)
			dat = top[-1][0]
			top.pop()
			fst = False

		elif m.group(IND_BRC) == '{':
			if not fst:
				raise Exception(
				"Unexpected token '{' in pos " + str(pos)
				)
			dat = dict(); top.append([dat, None])
			fst = True
			continue

		elif m.group(IND_BRC) == '[':
			if not fst:
				raise Exception(
				"Unexpected token '[' in pos " + str(pos)
				)
			dat = list(); top.append([dat])
			fst = True
			continue

		#Проверяем данные:
		elif m.group(IND_BOOL):
			#bool
			dat = (m.group(IND_BOOL) == 'true')
			fst = False
		elif m.group(IND_NULL):
			#null
			fst = False
			dat = None
		elif m.group(IND_NUM):
			#num
			if m.group(IND_NUM_FRAC):
				dat = float(m.group(IND_DATA))
			else:
				dat = int(m.group(IND_DATA))
			fst = False
		elif m.group(IND_STR):
			#str
			dat = str(m.group(IND_STR_CHAR))
			fst = False

		#Проверяем разделители:
		if   m.group(IND_COM) == ',':
			if fst or not top or (type(top[-1][0]) not in (dict, list)):
				pos = m.start(IND_COM)
				raise Exception(
				'Unexpected token \',\' in pos ' + str(pos)
				)
			fst = True
			continue
		elif m.group(IND_COL) == ':':
			if not top or type(top[-1][0]) is not dict:
				pos = m.start(IND_COL)
				raise Exception(
				'Unexpected token \':\' in pos ' + str(pos)
				)
			if type(dat) is not str:
				raise Exception(
				'Incorrect type of key in pos ' + str(pos)
				)
				pass
			top[-1][1] = dat
			fst = True
			continue

		#Проверяем вышестояющий объект:
		if not top:
			continue
		elif type(top[-1][0]) is list:
			top[-1][0].append(dat)
		elif type(top[-1][0]) is dict:
			key = top[-1][1]
			top[-1][0][key] = dat

	if top:
		raise Exception(
		'Unexpected end of string in pos ' + str(pos)
		)

	return dat
