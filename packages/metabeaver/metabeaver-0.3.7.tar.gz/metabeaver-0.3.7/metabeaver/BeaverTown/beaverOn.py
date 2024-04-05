def sumTwo(a, b):

    return a + b


class BeaverWorker:

    # Instantiate the class
    def __init__(self, name, baseFunction, baseArgs):

        self.name = name
        self.baseFunction = baseFunction
        self.baseArgs = baseArgs

    def runFunction(self, *args):

        self.result = self.baseFunction(*self.baseArgs)
        print(f"{self.name} says: {self.result}")
        if args:
            print(f'{self.name} also says: ')
            for arg in args:
                print(arg)

    def beaverPoem(self):

        # Replace with call to OpenAI
        print("Roses are red, beaver teeth are orange - it's true; beavers build dams and chew on wood too")


elongatedMuskrat = BeaverWorker('Elon',
                                sumTwo,
                                [5, 6]
                                )

elongatedMuskrat.runFunction('Want to buy a ticket to Mars?')