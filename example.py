import json
from deepnest import *

def print_dfs(obj):
	for i in obj: print(obj.level(), ': ', i)

def test1():
	print_dfs(DeepIterator("abcxyz"))
	print_dfs(DeepIterator(-9.05))
	print_dfs(DeepIterator(False))
	print_dfs(DeepIterator(True))
	print_dfs(DeepIterator(None))

def test2():
	a = [1, 2, {'a': True, 'b': False}, [3, 4, 5], 6]
	print_dfs(DeepIterator(a))

def test3():
	a = []
	for i in range(5): a = [i, a]
	print_dfs(DeepIterator(a))

def test4():
	a = []
	for i in range(1000): a = [i, a]
	b = []
	for i in range(1000): b = [i, b]
	try:
		print(a == b)
	except RecursionError:
		print('NO:(')
	a = DeepWrapper(a)
	b = DeepWrapper(b)
	print(a == b)
	print(a != b)
	b.obj[0] = None
	print(a == b)
	print(a != b)

def test5():

	def check(a):
		s = dumps(a)
		b = loads(s)
		print(
			a, ' -> ', s, ' -> ', b
		)

	check("abcxyz")
	check("\\\"")
	check(-9.05)
	check(-1)
	check(False)
	check(True)
	check(None)
	check(())
	check([])
	check({})

def test6():
	a = {
		'a': False,
		'b': True,
		'c': [
			1,
			{
				'd': "abc+@#!",
				'e': [2, 3, 4]
			},
			5
		],
		'f': {
			'g': -6.078,
			'i': 9
		},
		'j': None,
		'k': 0
	}
	print(a)
	s = dumps(a)
	print(s)
	b = loads(s)
	print(b)

def test7():
	a = []
	for i in range(1000): a = [i, a]
	try:
		s = json.dumps(a)
	except RecursionError:
		print('NO:(')
	s = dumps(a)
	print('YES!')
	try:
		b = json.loads(s)
	except RecursionError:
		print('NO:(')
	b = loads(s)
	print('YES!')

print('------------')
test1()
print('------------')
test2()
print('------------')
test3()
print('------------')
test4()
print('------------')
test5()
print('------------')
test6()
print('------------')
test7()
