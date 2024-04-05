# Create a class to encapsulate our Binary Search Tree
class BinarySearchTree:

    def __init__(self):
        self.root = None

    def insert(self, value):

        # Create a new Node which will hold the value passed to the insert method.
        new_node = Node(value)

        # Make the new node, with our value, the root, if and only there is no existing root.
        if self.root is None:
            self.root = new_node
        # If the root exists, do not insert yet, but assign the root node to current_node
        else:
            current_node = self.root

            # While the value is less than the value of the current node, traverse left or create new node left.
            while True:
                # Go left
                if value < current_node.value:
                    # Create a node to store our value if the value is less than current_node.value and no left child.
                    if current_node.left is None:
                        current_node.left = new_node
                        break
                    # Traverse left if value is less than current_node.value and left child of current_node exists.
                    else:
                        current_node = current_node.left
                # Go right
                else:
                    # If value is greater than or equal to the current_node.value and no right child, insert right.
                    if current_node.right is None:
                        current_node.right = new_node
                        break
                    # Traverse right if
                    else:
                        current_node = current_node.right

    # Traverse the tree in ascending order. Assumes the tree is a valid BST.
    def inorder(self):

        # Array to hold traversed elements after recursing through left most tree(s) as priority
        sorted_array = []

        # Traverse the tree in ascending order
        def in_order(node):
            if node is not None:
                in_order(node.left)
                sorted_array.append(node.value)
                in_order(node.right)

        # Start at the root node.
        in_order(self.root)

        return sorted_array

    def reverseInOrder(self):

        def reverseOrder(node):

            sorted = []

            if node is not None:
                reverseOrder(node.right)
                sorted.append(node.value)
                reverseOrder(node.left)

            reverseOrder(self.root)

        return sorted

    def median(self):
        sorted_array = self.traverse()

        # If the number of elements in the array is even, then the median is the average of the two middle elements.
        if len(sorted_array) % 2 == 0:
            median = (sorted_array[len(sorted_array) // 2] + sorted_array[len(sorted_array) // 2 - 1]) / 2
        else:
            # Otherwise, the median is the middle element. Uses floor to round down, and then index pos to reach middle.
            median = sorted_array[len(sorted_array) // 2]

        return median


# Define a node to be used in our binary structure.
class Node:

    # Hold the value the node was initiated with and instantiate None to the left AND right where future nodes may be.
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None