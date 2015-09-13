from kanjiQuestions import addJLPTKanjiToEnglish as addKanjiSet
from vocabQuestions import addVocabSet, addVocabSetShortcut
from japQuestions import addJapaneseQuestions
from quizBasics import SpacedQuestionSupplier as SpacedQs
from quizBasics import ReverseSpacedQuestionSupplier as ReverseQs

qs = {}
#orderedKanji = addKanjiSet(qs)
#orderedVocab = addVocabSetShortcut("vocabPickle.pkl", qs)
ordered, kanji, vocab, chunks = addJapaneseQuestions(qs, "vocabPickle.pkl")
keyVocabCards = [q for q in vocab if (q.startswith('vocabKS.') or
                                      q.startswith('vocabRS'))]
questionSupplier = ReverseQs(qs, ordered, "records.txt")
def counts():
    print("Kanji learned: %d / %d"%(questionSupplier.countCardSet(kanji),
                                    len(kanji)))
    print("Vocab learned: %d / %d (%d / %d cards)"%\
          (questionSupplier.countCardSet(keyVocabCards),
           len(keyVocabCards),
           questionSupplier.countCardSet(vocab),
           len(vocab)))
    for i in range(len(chunks)):
        chunk = chunks[i]
        cur, tot = questionSupplier.countCardSet(chunk), len(chunk)
        if cur != tot:
            chunkKanji = [q for q in chunk if q.startswith('kanji')]
            chunkVocab = [q for q in chunk if q.startswith('vocab')]
            chunkKeyVocab = [q for q in chunk if (q.startswith('vocabKS.') or
                                                  q.startswith('vocabRS'))]
            print("Current chunk: %d"%i)
            print("Cards in chunk: %d / %d"%(cur, tot))
            print("Kanji in chunk: %d / %d"%(
                questionSupplier.countCardSet(chunkKanji),
                len(chunkKanji)))
            print("Vocab in chunk: %d / %d (%d / %d cards)"%(
                questionSupplier.countCardSet(chunkKeyVocab),
                len(chunkKeyVocab),
                questionSupplier.countCardSet(chunkVocab),
                len(chunkVocab)))
            break

def main():
    counts()
    with questionSupplier:
        questionSupplier.askManyQuestions()
    counts()

print("Ready")
