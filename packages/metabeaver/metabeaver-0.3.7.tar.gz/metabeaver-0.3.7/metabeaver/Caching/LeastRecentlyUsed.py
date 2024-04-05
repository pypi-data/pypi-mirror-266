class LRUCache:

    def __init__(self, capacity: int):
        """
        Initialize an LRU cache with a given capacity.

        Args:
            capacity (int): The maximum number of key-value pairs the cache can hold.
        """
        self.capacity = capacity
        self.cache = {}
        self.order = []

    def get(self, key: int) -> int:
        """
        Retrieve the value associated with a given key from the cache.

        Args:
            key (int): The key to retrieve.

        Returns:
            int: The value associated with the key or -1 if the key is not found.
        """
        if key in self.cache:
            # Move the accessed key to the end of the order list
            self.order.remove(key)
            self.order.append(key)
            return self.cache[key]
        return -1

    def put(self, key: int, value: int):
        """
        Insert or update the value for a given key in the cache. If the number of keys exceeds
        the capacity, remove the least recently used key.

        Args:
            key (int): The key to insert or update.
            value (int): The value associated with the key.
        """
        if key in self.cache:
            # Key exists, update the value and move it to the end of the order list
            self.cache[key] = value
            self.order.remove(key)
            self.order.append(key)
        else:
            if len(self.cache) >= self.capacity:
                # Remove the least recently used key and its associated value
                lru_key = self.order.pop(0)
                del self.cache[lru_key]
            self.cache[key] = value
            self.order.append(key)

# Example usage:
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # Output: 1
cache.put(3, 3)      # Evicts key 2
print(cache.get(2))  # Output: -1 (not found)
cache.put(4, 4)      # Evicts key 1
print(cache.get(1))  # Output: -1 (not found)
print(cache.get(3))  # Output: 3
print(cache.get(4))  # Output: 4
