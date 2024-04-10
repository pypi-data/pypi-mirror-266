import time
def sparta_2d88b72969():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_2d88b72969()
def sparta_5c3a8bdc2f(tempBool=True):
	A=next(TicToc)
	if tempBool:print('Elapsed time: %f seconds.\n'%A);return A
def sparta_4a1af72140():sparta_5c3a8bdc2f(False)