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
			s += "Order "+str(i)+":\n"
			for cont in self.orders[i].contexts:
				if(i > 0):
					s += "  '"+cont+"':\n"
				for char in self.orders[i].contexts[cont].chars:
					s += "     '"+char+"': "+str(self.orders[i].contexts[cont].chars[char])+"\n"
			s += "\n"
		print(s)

	# print a specific order of the model
	# TODO: Output becomes too long, reordering on the screen has to be made
	def printOrder(self, n):
		s = "Total characters in this order: "+str(self.orders[n].cnt)+"\n"
		s += "Order "+str(n)+":\n"
		for cont in self.orders[n].contexts:
			if(n > 0):
				s += "  '"+cont+"':\n"
			for char in self.orders[n].contexts[cont].chars:
				s += "     '"+char+"': "+str(self.orders[n].contexts[cont].chars[char])+"\n"
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
				return 1/self.alphSize
			return self.p(c, cont[1:])

		context = order.contexts[cont]
		if not context.hasChar(c):
			if (order.n == 0):
				return 1/self.alphSize
			return self.p(c, cont[1:])
		return context.getCharCount(c)/order.cnt

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
	def __init__(self):
		self.chars = {}

	def hasChar(self, c):
		return c in self.chars

	def addChar(self, c):
		self.chars[c] = 0

	def incCharCount(self, c):
		self.chars[c] += 1

	def getCharCount(self, c):
		return self.chars[c]

	def merge(self, cont):
		for c in cont.chars:
			if not self.hasChar(c):
				self.chars[c] = cont.chars[c]
			else:
				self.chars[c] += cont.chars[c]

	def negate(self, cont):
		for c in cont.chars:
			if (not self.hasChar(c)) or (self.chars[c] < cont.chars[c]):
				raise NameError("Model1 does not contain the Model2 to be negated, Model1 might be corrupted!")
			else:
				self.chars[c] -= cont.chars[c]
		empty = [c for c in self.chars if self.chars[c] == 0]
		for c in empty:
			del self.chars[c]