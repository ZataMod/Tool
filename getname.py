import glob
n=list('123456789')
for i in n:
	for name in glob.glob(i+'*.jpg'):
		if len(name)==9:
			print(name[:-4])
input()