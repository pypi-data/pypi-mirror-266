import pickle
import datetime as dt

# Function to save object, using pickle, with timestamp
def save_object(obj):
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"object_{timestamp}.pkl"
    with open(filename, "wb") as f:
        pickle.dump(obj, f)
    print(f"Object saved to {filename}")



























