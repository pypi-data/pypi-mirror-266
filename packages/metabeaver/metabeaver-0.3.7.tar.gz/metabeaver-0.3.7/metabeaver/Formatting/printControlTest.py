from metabeaver.Formatting.printControl import conditional_print as cprint


import os


# Usage example:
def yesPrint():

    # Update BEAVER_PRINTING to be True. str type because we are creating an env var.
    os.environ["BEAVER_PRINTING"] = 'True'

    cprint('Inside yesPrint!')
    # Rest of your code


def noPrint():

    # Update BEAVER_PRINTING to be False. str type because we are creating an env var.
    os.environ["BEAVER_PRINTING"] = 'False'

    cprint('Inside noPrint!')
    # Rest of your code


def someFunction(argOne, argTwo):

    cprint('Roses are red, Violets are blue, Beaver teeth are orange and they chew through wood too!')


# Set the environment variable to str 'True' and print
os.environ["BEAVER_PRINTING"] = 'True'
someFunction('', '')

# Set the environment variable to str 'False' and do not print. Call function that does not set value internally.
os.environ["BEAVER_PRINTING"] = 'False'
someFunction('', '')

# Call functions which modify printing within themselves
yesPrint()
noPrint()