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

	#TODO: ...

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
		if type(i) is None:
			ans += 'null'
	while top:
		ans += top[-1]
		top.pop()

	return ans

#TODO: loads(...)
