#Итератор для обхода в глубину сильно вложенных объектов:
class DeepIterator:

	class Pair:
		def __init__(self, key, val):  self.key, self.val = key, val
		def __str__(self): return str((self.key, self.val))

	def __init__(self, obj):
		self.top = [[(obj,), 0]]
		self.obj = None

	def __next__(self):

		while self.top and self.top[-1][1] >= len(self.top[-1][0]):
			self.top.pop()

		if not self.top:
			raise StopIteration()

		buf = self.top[-1]
		if len(buf) == 3:
			key = buf[2][buf[1]]
			obj = buf[0][key]
			self.obj = DeepIterator.Pair(key, obj)
		else:
			pos = buf[1]
			obj = buf[0][pos]
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

		lhs = DeepIterator(self.obj); rhs = DeepIterator(rhs.obj)
		for itl, itr in zip(lhs, rhs):
			if lhs.level() != rhs.level(): return False
			if type(itl) is not type(itr): return False
			if type(itl) is DeepIterator.Pair:
				if itl.key != itr.key:
					return False
				vl = itl.val; vr = itr.val
				if type(vl) is not type(vr):
					return False
				itl = vl; itr = vr
			if type(itl) in (
			str, float, int, bool, None
			):
				if itl != itr:
					return False

		try: next(lhs)
		except StopIteration: enl = True
		else: enl = False
		try: next(rhs)
		except StopIteration: enr = True
		else: enr = False

		return enl and enr

	#TODO: ...
