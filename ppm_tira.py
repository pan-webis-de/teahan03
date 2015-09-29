from model import Model
from sys import argv
from math import log
import pickle, os
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
		m = Model(5, 256)
		print("creating model for "+cand)
		for doc in jsonhandler.trainings[cand]:
			m.read(jsonhandler.getTrainingText(cand, doc))
			print(doc+" read")
		storeModel(m, os.path.join(modeldir, cand))
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


def main():
	if len(argv) != 2:
		print("Syntax: python ppm_tira.py MAIN_FOLDER")
		return

	corpusdir = argv[1]
	jsonhandler.loadJson(corpusdir)

	global modeldir
	modeldir = os.path.join(corpusdir, MODEL_DIR)
	if not os.path.exists(modeldir):
		os.makedirs(modeldir)
		createModels()	
	loadModels()
	
	createAnswers()
	jsonhandler.storeJson(unknowns, authors, scores, corpusdir)
	
modeldir = ""
models = {}

candidates = jsonhandler.candidates
unknowns = jsonhandler.unknowns
authors = []
scores = []

main()

