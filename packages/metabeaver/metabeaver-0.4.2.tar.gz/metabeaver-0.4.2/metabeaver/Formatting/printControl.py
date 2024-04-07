import os


def conditional_print(message):

    # Try to get a boolean BEAVER_PRINTING operating system variable
    try:
        beaverPrint = os.environ.get("BEAVER_PRINTING")
    # If we can not find the BEAVER_PRINTING variable, assume printing is not wanted
    except Exception as e:
        beaverPrint = False

    # Print if we enabled BEAVER_PRINTING by setting it to True
    if beaverPrint == 'True':
        print(message)