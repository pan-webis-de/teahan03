from math import log
import pickle, os, argparse
import jsonhandler

MODEL_DIR = "models"

class Model(object):
	# cnt - count of characters read
	# modelOrder - order of the model
	# orders - List of Order-Objects
	# alphSize - size of the alphabet
	def __init__(self, order, alphSize):
		self.cnt = 0
		self.alphSize = alphSize
		self.modelOrder = order
		self.orders = []
		for i in range(order+1):
			self.orders.append(Order(i))

	# print the model
	# TODO: Output becomes too long, reordering on the screen has to be made		
	def printModel(self):
		s = "Total characters read: "+str(self.cnt)+"\n"
		for i in range(self.modelOrder+1):
			self.printOrder(i)

	# print a specific order of the model
	# TODO: Output becomes too long, reordering on the screen has to be made
	def printOrder(self, n):
		o = self.orders[n]
		s = "Order "+str(n)+": ("+str(o.cnt)+")\n"
		for cont in o.contexts:
			if(n > 0):
				s += "  '"+cont+"': ("+str(o.contexts[cont].cnt)+")\n"
			for char in o.contexts[cont].chars:
				s += "     '"+char+"': "+str(o.contexts[cont].chars[char])+"\n"
		s += "\n"
		print(s)

	# updates the model with a character c in context cont
	def update(self, c, cont):
		if len(cont) > self.modelOrder:
			raise NameError("Context is longer than model order!")
			
		order = self.orders[len(cont)]
		if not order.hasContext(cont):
			order.addContext(cont)
		context = order.contexts[cont]
		if not context.hasChar(c):
			context.addChar(c)
		context.incCharCount(c)
		order.cnt += 1
		if (order.n > 0):
			self.update(c, cont[1:])
		else:
			self.cnt += 1

	# updates the model with a string
	def read(self, s):
		if (len(s) == 0):
			return
		for i in range(len(s)):
			cont = ""
			if (i != 0 and i - self.modelOrder <= 0):
				cont = s[0:i]
			else:
				cont = s[i - self.modelOrder:i]
			self.update(s[i], cont)

	# return the models probability of character c in content cont
	def p(self, c, cont):
		if len(cont) > self.modelOrder:
			raise NameError("Context is longer than order!")

		order = self.orders[len(cont)]
		if not order.hasContext(cont):
			if (order.n == 0):
				return 1.0/self.alphSize
			return self.p(c, cont[1:])

		context = order.contexts[cont]
		if not context.hasChar(c):
			if (order.n == 0):
				return 1.0/self.alphSize
			return self.p(c, cont[1:])
		return float(context.getCharCount(c))/context.cnt
	
	# merge this model with another model m, esentially the values for every character in every context are added
	def merge(self, m):
		if self.modelOrder != m.modelOrder:
			raise NameError("Models must have the same order to be merged")
		if self.alphSize != m.alphSize:
			raise NameError("Models must have the same alphabet to be merged")
		self.cnt += m.cnt
		for i in range(self.modelOrder+1):
			self.orders[i].merge(m.orders[i])

	# make this model the negation of another model m, presuming that this model was made my merging all models
	def negate(self, m):
		if self.modelOrder != m.modelOrder or self.alphSize != m.alphSize or self.cnt < m.cnt:
			raise NameError("Model does not contain the Model to be negated")
		self.cnt -= m.cnt
		for i in range(self.modelOrder+1):
			self.orders[i].negate(m.orders[i])

class Order(object):
	# n - whicht order
	# cnt - character count of this order
	# contexts - Dictionary of contexts in this order
	def __init__(self, n):
		self.n = n
		self.cnt = 0
		self.contexts = {}
	
	def hasContext(self, context):
		return context in self.contexts

	def addContext(self, context):
		self.contexts[context] = Context()

	def merge(self, o):
		self.cnt += o.cnt
		for c in o.contexts:
			if not self.hasContext(c):
				self.contexts[c] = o.contexts[c]
			else:
				self.contexts[c].merge(o.contexts[c])
	def negate(self, o):
		if self.cnt < o.cnt:
			raise NameError("Model1 does not contain the Model2 to be negated, Model1 might be corrupted!")
		self.cnt -= o.cnt
		for c in o.contexts:
			if not self.hasContext(c):
				raise NameError("Model1 does not contain the Model2 to be negated, Model1 might be corrupted!")
			else:
				self.contexts[c].negate(o.contexts[c])
		empty = [c for c in self.contexts if len(self.contexts[c].chars) == 0]
		for c in empty:
			del self.contexts[c]

class Context(object):
	# chars - Dictionary containing character counts of the given context
	# cnt - character count of this context
	def __init__(self):
		self.chars = {}
		self.cnt = 0

	def hasChar(self, c):
		return c in self.chars

	def addChar(self, c):
		self.chars[c] = 0

	def incCharCount(self, c):
		self.cnt += 1
		self.chars[c] += 1

	def getCharCount(self, c):
		return self.chars[c]

	def merge(self, cont):
		self.cnt += cont.cnt
		for c in cont.chars:
			if not self.hasChar(c):
				self.chars[c] = cont.chars[c]
			else:
				self.chars[c] += cont.chars[c]

	def negate(self, cont):
		if self.cnt < cont.cnt:
			raise NameError("Model1 does not contain the Model2 to be negated, Model1 might be corrupted!")
		self.cnt -= cont.cnt
		for c in cont.chars:
			if (not self.hasChar(c)) or (self.chars[c] < cont.chars[c]):
				raise NameError("Model1 does not contain the Model2 to be negated, Model1 might be corrupted!")
			else:
				self.chars[c] -= cont.chars[c]
		empty = [c for c in self.chars if self.chars[c] == 0]
		for c in empty:
			del self.chars[c]


# returns model object loaded from 'mpath' using pickle
def loadModel(mpath):
	f = open(mpath, "rb")
	m = pickle.load(f)
	f.close()
	return m

# stores model object 'model' to 'mpath' using pickle
def storeModel(model, mpath):
	f = open(mpath, "wb")
	pickle.dump(model, f)
	f.close()

# calculates the cross-entropy of the string 's' using model 'm'
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

# loads models of candidates in 'candidates' into 'models'
def loadModels():
	for cand in jsonhandler.candidates:
		print("loading model for "+cand)
		models[cand] = loadModel(os.path.join(modeldir, cand))

# creates models of candidates in 'candidates'
# updates each model with any files stored in the subdirectory of 'corpusdir' named with the candidates name
# stores each model named under the candidates name in 'modeldir'
def createModels():
	jsonhandler.loadTraining()
	for cand in candidates:
		models[cand] = Model(5, 256)
		print("creating model for "+cand)
		for doc in jsonhandler.trainings[cand]:
			models[cand].read(jsonhandler.getTrainingText(cand, doc))
			print(doc+" read")
		#storeModel(models[cand], os.path.join(modeldir, cand))
		#print("Model for "+cand+" saved")

# attributes the authorship, according to the cross-entropy ranking.
# attribution is saved in json-formatted structure 'answers'
def createAnswers():
	print("creating answers")
	for doc in unknowns:
		hs = []
		for cand in candidates:
			hs.append(h(models[cand], jsonhandler.getUnknownText(doc)))
		m = min(hs)
		author = candidates[hs.index(m)]
		hs.sort()
		score = (hs[1]-m)/(hs[len(hs)-1]-m)

		authors.append(author)
		scores.append(score)
		print(doc+" attributed")

# commandline argument parsing, calling the necessary methods
def main():
	
	parser = argparse.ArgumentParser(description="Tira submission for PPM approach (teahan03)")
	parser.add_argument("-i", action="store", help="path to corpus directory")
	parser.add_argument("-o", action="store", help="path to output directory")
	args = vars(parser.parse_args())

	corpusdir = args["i"]
	outputdir = args["o"]
	if corpusdir == None or outputdir == None:
		parser.print_help()
		return

	jsonhandler.loadJson(corpusdir)

	global modeldir
	modeldir = os.path.join(outputdir, MODEL_DIR)
	if not os.path.exists(modeldir):
		#os.makedirs(modeldir)
		createModels()
	else:
		loadModels()
	
	createAnswers()
	jsonhandler.storeJson(outputdir, unknowns, authors, scores)

# initialization of global variables
modeldir = ""
models = {}

candidates = jsonhandler.candidates
unknowns = jsonhandler.unknowns
authors = []
scores = []

main()

