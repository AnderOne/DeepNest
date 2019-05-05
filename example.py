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
	b.obj[0] = None
	print(a == b)

print('------------')
test1()
print('------------')
test2()
print('------------')
test3()
print('------------')
test4()
