CORPRORA:
C10
C50
PAN11small
PAN11large
PAN12A
PAN12B
PAN12C
PAN12D
PAN12I
PAN12J


The files for each corpus are located in a MAIN_FOLDER. Within this folder there is a file meta-file.json with the following information:

a) The language of texts (e.g., EN, GR, etc.)
b) The candidate author names. For each candidate author there is a folder within MAIN_FOLDER containing all available texts by that author.
c) The folder (sub-folder of MAIN_FOLDER) of texts of unknown authorship to be used for evaluation. 
d) The names of the unknown texts.

TIRA instructions
An authorship attribution system in TIRA should accept as input the MAIN_FOLDER of the corpus and produce an output in JSON as follows:

{
"answers": [
	{"unknown_text": "unknownX", "author": "candidateY", "score": Z},
	...
	]
}

where "unknownX" is the name of an unknown text (from meta-file.json), "candidateY" is the name of a candidate author (from meta-file.json) and Z is a real score in [0,1] indicating the confidence of the answer (0 means completely uncertain, 1 means completely sure). In the case of open-set classification, when it is estimated that none of the candidate authors is the author of the unknown text "candidateY" should be set to "candidate00000". For example:

{
"answers": [
	{"unknown_text": "unknown00001.txt", "author": "candidate00001", "score": 0.8},
	{"unknown_text": "unknown00002.txt", "author": "candidate00000", "score": 0.9},
	...
	]
}
