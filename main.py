from model import Model
from sys import argv
from math import log
import pickle

def loadModel(fname):
	f = open(fname, "rb")
	m = pickle.load(f)
	f.close()
	return m

def storeModel(model, fname):
	f = open(fname, "wb")
	pickle.dump(model, f)
	f.close()

def createModel(fname, order, alphSize):
	storeModel(Model(order, alphSize), fname)

def readFile(document, modelfname):
	f = open(document, "r")
	s = f.read()
	f.close()
	m = loadModel(modelfname)
	m.read(s)
	storeModel(m, modelfname)

def h(m, s):
	n = len(s)
	h = 0
	for i in range(n):
		if i == 0:
			context = ""
		elif i <= m.modelOrder:
			context = s[0:i]
		else:
			context = s[i - m.modelOrder:i]
		h -= log(m.p(s[i], context), 2)
	return h/n
	
def crossEntropy(document, modelfname):
	f = open(document, "r")
	s = f.read()
	f.close()
	m = loadModel(modelfname)
	return h(m, s)

def merge(m1fname, m2fname):
	m1 = loadModel(m1fname)
	m2 = loadModel(m2fname)
	m1.merge(m2)
	storeModel(m1, m1fname)

def complement(modelfname, universefname, complementfname):
	m = loadModel(modelfname)
	u = loadModel(universefname)
	u.negate(m)
	storeModel(u, complementfname)

def main():
	argc = len(argv)
	if argc == 1:
		exit(0)
	if argv[1] == "readfile":
		if argc == 4:
			readFile(argv[2], argv[3])
		else:
			print("Syntax: readfile document model")
			exit(0)
		print("File "+argv[2]+" sucessfully read by model "+argv[3])
	elif argv[1] == "create":
		if argc == 5:
			createModel(argv[2], int(argv[3]), int(argv[4]))
		else:
			print("Syntax: create model order alphabetsize")
			exit(0)
		print("Model "+argv[2]+" sucessfully created (order: "+argv[3]+", alphabet size: "+argv[4]+")")
	elif argv[1] == "crossentropy":
		h = 0
		if argc == 4:
			h = crossEntropy(argv[2], argv[3])
		else:
			print("Syntax: crossentropy document model")
			exit(0)
		print(str(h))
	elif argv[1] == "merge":
		if argc == 4:
			mergeModels(argv[2], argv[3])
		else:
			print("Syntax: merge model1 model2")
			exit(0)
		print("Models successfully merged in "+argv[2])
	elif argv[1] == "complement":
		if argc == 5:
			negateModel(argv[2], argv[3], argv[4])
		else:
			print("Syntax: complement model universe complementname")
			exit(0)
		print("Complement of Model "+argv[2]+" stored in "+argv[4])
	else:
		print("Invalid syntax")
		exit(0)

main()

