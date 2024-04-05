from metabeaver.BeaverTown.abstractBeaver import AbstractBeaver

"""
Here we will write a control flow function detailing the difference between if-elif-else and if-if-else.

Beneath the moon's soft and silvery sheen,
Harry the Beaver roams with mischief keen.
To the farmer's shed with whisker's unfurled,
Wood thievery in the midnight world.

Paintball bullets, a short and vibrant array,
Red and blue hues lit up in the moonlit fray.
Harry fled, woodless, into the night,
A tale of mischief, a colorful flight.

"""

harryTheBeaver = AbstractBeaver('Harry', ['red', 'blue'], 3)
coloursOfHarry = harryTheBeaver.getColour()

# Scenario 1: Using if-not-then logic: one if, else-if, and else
# The following code will print red, because it will find red, then only check for blue (else-if) if red was not found.
print('Check for one colour of our kleptomanic beaver...')
if "red" in coloursOfHarry: # Check for "red"
    print("Roses are red, and Harry is too...")
elif "blue" in coloursOfHarry: # Check for "blue"
    print("You won't see this line but he is feeling quite blue!")
else: # Does not print because at least one of the above conditions, find red, was true.
    print("Harry's adventures were but a dream: Harry's at home, snoring, and rather clean")

# Scenario 2: Using if this OR if this OR if-not-any logic: TWO if statements and ONE else
# The following code will print red, because it will find red, then only check for blue (else-if) if red was not found.
print('Check both colours of our kleptomanic beaver, one after the other...')
if "red" in coloursOfHarry: # Check for "red"
    print("Roses are red, and Harry is too...")
if "blue" in coloursOfHarry: # Check for "blue"
    print("He got shot and is feeling quite blue!")
else: # Does not print because at least one of the above conditions, find red, was true.
    print("Harry's adventure's were but a dream: Harry's at home, snoring, and rather clean")

# Scenario 3: If no if statements execute, revert to "now do this", the 'else' statement
# The following code will print the else statement, because Harry was not shot
harryTheBeaver = AbstractBeaver('Harry', ['yellow', 'yellow'], 3)
if "red" in coloursOfHarry: # Check for "red"
    print("Roses are red but Harry is yellow...") # Will not be found, so will not print
elif "blue" in coloursOfHarry: # Check for "blue"
    print("He glows in the night, a vibrant fellow...") # Harry is very fashionable.
else: # Will print because neither of the above conditions evaluated
    print("Harry looks like a duck and is not feeling mellow.")