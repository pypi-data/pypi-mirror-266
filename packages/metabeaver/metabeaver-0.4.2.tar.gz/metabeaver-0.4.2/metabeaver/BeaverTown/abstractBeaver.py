# Define an etheral beaver, a base class with a few limited features we could extend to more specific beaver types.
class AbstractBeaver:

    # Expects a str, list of string, and an int to set our beaver features.
    def __init__(self, name, colours, age):

        self.name = name
        self.colours = colours
        self.age = age

    # Returns the list of colours of our AbstractBeaver.
    def getColour(self):
        return self.colours






























