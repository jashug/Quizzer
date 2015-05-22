from kanjiQuestions import addJLPTKanjiToEnglish as addKanjiSet
from vocabQuestions import addVocabSet, addVocabSetShortcut
from japQuestions import addJapaneseQuestions
from quizBasics import SpacedQuestionSupplier as SpacedQs
from quizBasics import ReverseSpacedQuestionSupplier as ReverseQs

qs = {}
#orderedKanji = addKanjiSet(qs)
#orderedVocab = addVocabSetShortcut("vocabPickle.pkl", qs)
#keyVocabCards = [q for q in orderedVocab if (q.startswith('vocabKS.') or
#                                             q.startswith('vocabRS'))]
ordered = addJapaneseQuestions(qs, "vocabPickle.pkl")
questionSupplier = ReverseQs(qs, ordered, "records.txt")
def counts():
    print "Kanji learned: %d / %d"%(questionSupplier.countCardSet(orderedKanji),
                                    len(orderedKanji))
    print "Vocab learned: %d / %d (%d / %d cards)"%\
          (questionSupplier.countCardSet(keyVocabCards),
           len(keyVocabCards),
           questionSupplier.countCardSet(orderedVocab),
           len(orderedVocab))

def main():
    #counts()
    with questionSupplier:
        questionSupplier.askManyQuestions()
    #counts()

main()
