import pickle as pickle
from vocabQuestions import addVocabSet
qs = {}
ordered = addVocabSet(qs)
with open("vocabPickle.pkl", 'wb') as f:
    pickle.dump((qs, ordered), f, -1)
