class MyQueue:


    def __init__(self):

        self.theQueue = []


    def enqueue(self, x: int) -> None:

        self.theQueue = [x] + self.theQueue


    def dequeue(self) -> int:

        queueLength = len(self.theQueue)
        lastElement = self.theQueue[-1]
        self.theQueue = self.theQueue[0:queueLength-1]
        print(self.theQueue)

        return lastElement