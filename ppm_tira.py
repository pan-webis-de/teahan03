from model import Model
from math import log
import pickle, os, argparse
import jsonhandler

MODEL_DIR = "models"

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
		storeModel(models[cand], os.path.join(modeldir, cand))
		print("Model for "+cand+" saved")

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
		os.makedirs(modeldir)
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

