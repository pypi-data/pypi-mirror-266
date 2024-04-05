import os
import pickle


# To use this function, simply pass your dictionary and the desired filename as arguments:
def save_dict_to_pickle(dictionary: dict, filename: str) -> None:
    """
    Save a dictionary to a pickle file in the current working directory.
    Args:
        dictionary (dict): The dictionary to be saved.
        filename (str): The name of the pickle file.
    """

    # Ensure the filename has a .pkl extension
    if not filename.endswith(".pkl"):
        filename += ".pkl"

    # Get the current working directory
    cwd = os.getcwd()
    filepath = os.path.join(cwd, filename)

    # Save the dictionary to the pickle file
    with open(filepath, 'wb') as file:
        pickle.dump(dictionary, file)

# Example
#my_dict = {'key1': 1, 'key2': 2, 'key3': 3}
#save_dict_to_pickle(my_dict, 'my_dict.pkl')