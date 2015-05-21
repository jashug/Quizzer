import time
from heap import Heap
import base64

def uid(s):
    """Generate a unique ASCII string for a unicode string."""
    return base64.urlsafe_b64encode(s.encode("UTF-8"))

def uidInv(s):
    """uidInv(uid(s)) == s"""
    return base64.urlsafe_b64decode(s).decode("UTF-8")

class Record(object):
    def __init__(self, tag, answer, time, dt, grade):
        self.q, self.ans = tag, answer
        self.time, self.dt, self.grade = time, dt, grade

    def __str__(self):
        return "%(tag)s %(time).3f %(dt).3f %(grade)s %(ans)s\n"%{
            'tag':self.q, 'time':self.time, 'dt':self.dt,
            'grade':'1' if self.grade else '0', 'ans':uid(self.ans)}

    @staticmethod
    def fromStringUnencoded(line):
        assert line[-1] == '\n'
        l = line[:-1].split(' ')
        return Record(l[0], ' '.join(l[4:]),
                      float(l[1]), float(l[2]), l[3] == '1')

    @staticmethod
    def fromString(line):
        assert line[-1] == '\n'
        l = line[:-1].split(' ')
        assert len(l) == 5
        return Record(l[0], uidInv(l[4]),
                      float(l[1]), float(l[2]), l[3] == '1')

class QuestionSupplier(object):
    def __init__(self, qs, ordered, backingFileName):
        self.qs = qs
        self.ordered = ordered
        self.orderedI = 0
        self.seen = set()
        self.backingFileName = backingFileName
        self.outFile = None
        try:
            with open(backingFileName, 'r') as inFile:
                for line in inFile:
                    self.record(Record.fromString(line))
        except IOError:
            pass

    def __enter__(self):
        self.outFile = open(self.backingFileName, 'a')
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.outFile.close()
        self.outFile = None

    def record(self, record):
        """Saves a record. If in a with block, saves record to outFile"""
        if record.q not in self.qs: return
        if self.outFile is not None:
            self.outFile.write(str(record))
        self.seen.add(record.q)

    def nextNewQuestion(self):
        while (self.orderedI < len(self.ordered) and
               self.ordered[self.orderedI] in self.seen):
            self.orderedI += 1
        return (self.ordered[self.orderedI]
                if self.orderedI < len(self.ordered)
                else None)

    def askOneQuestion(self):
        q = self.nextQuestion()
        if q is None:
            print "NO QUESTION"
            return
        if q not in self.qs:
            print "NOT RECOGNIZED: %s"%str(q)
            return
        if q not in self.seen:
            print "New Question:"
            self.qs[q].body()
        self.qs[q].ask()
        start = time.time()
        ans = raw_input()
        end = time.time()
        grade = self.qs[q].check(ans)
        if grade:
            print "Correct!"
        else:
            print "Incorrect!"
            print "Remember:"
            self.qs[q].body()
        self.record(Record(q, ans, start, end - start, grade))
        return grade

    def askManyQuestions(self):
        assert self.outFile is not None
        print "Welcome to the Quiz program!"
        self.stats()
        raw_input("Press enter to begin.")
        start = time.time()
        total = 0
        wrong = 0
        while True:
            grade = self.askOneQuestion()
            total += 1
            if not grade: wrong += 1
            if raw_input("Continue? (non-empty to stop): "):
                break
        end = time.time()
        dt = end - start
        self.stats()
        print "You missed %d problems." % wrong
        print "You answered %d problems in %d minutes %d seconds." %\
              (total, dt // 60, dt % 60)
        print "That is %.3f seconds per problem, or %.3f problems per minute" %\
              (dt / total, 60 * total / dt)

    def stats(self):
        print "You have learned %d cards." % self.cardsSeen()

    def countCardSet(self, cards):
        return len([c for c in cards if c in self.seen])

    def cardsSeen(self):
        return len(self.seen)

class SpacedQuestionSupplier(QuestionSupplier):
    def __init__(self, qs, ordered, backingFileName):
        self.queue = Heap()
        self.lastTimes = {}
        self.alpha = 2
        self.beta = 4
        self.baseInterval = 10
        QuestionSupplier.__init__(self, qs, ordered, backingFileName)
    
    def record(self, record):
        QuestionSupplier.record(self, record)
        if record.q not in self.qs: return
        if record.grade and record.q in self.lastTimes:
            lastTime, lastInterval = self.lastTimes[record.q]
            interval = min(self.alpha * (record.time - lastTime),
                           self.beta * lastInterval)
            if interval < lastInterval: interval = lastInterval
        else:
            interval = self.baseInterval
        self.queue.put(record.q, record.time + interval)
        self.lastTimes[record.q] = (record.time, interval)

    def nextQuestion(self):
        if len(self.queue) > 0 and (self.queue.peek()[0] <= time.time() or
                                    self.nextNewQuestion() is None):
            return self.queue.peek()[1]
        else:
            return self.nextNewQuestion()

class ReverseSpacedQuestionSupplier(SpacedQuestionSupplier):
    def __init__(self, qs, ordered, backingFileName):
        self.revQueue = Heap()
        SpacedQuestionSupplier.__init__(self, qs, ordered, backingFileName)

    def record(self, record):
        SpacedQuestionSupplier.record(self, record)
        if record.q in self.revQueue: self.revQueue.remove(record.q)
        #assert len(self.seen) == len(self.revQueue) + len(self.queue)

    def nextQuestion(self):
        while len(self.queue) > 0 and self.queue.peek()[0] <= time.time():
            t, q = self.queue.pop()
            self.revQueue.put(q, -t)
        if len(self.revQueue) > 0:
            assert -self.revQueue.peek()[0] <= time.time()
            return self.revQueue.peek()[1]
        newQ = self.nextNewQuestion()
        if newQ is not None:
            return newQ
        if len(self.queue) > 0:
            return self.queue.peek()[1]
        return None

    def stats(self):
        SpacedQuestionSupplier.stats(self)
        self.nextQuestion()
        print "Review queue: %d" % len(self.revQueue)
##        if len(self.queue):
##            print "Forwards queue: %d" % len(self.queue)
##            print "Next expiring: %.3f" % self.queue.peek()[0]
##            print "Current time: %.3f" % time.time()
