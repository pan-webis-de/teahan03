from model import Model as Model, Order, Context
import pickle

def loadModel(name, v):
	f = open(name+"_"+v+".model", "rb")
	m = pickle.load(f)
	f.close()
	return m

def storeModel(model, name, v):
	f = open(name+"_"+v+".model", "wb")
	pickle.dump(model, f)
	f.close()


#storeModel(m, "ppm", "1")
m = loadModel("ppm", "1")
m.printModel()
#print(m)

