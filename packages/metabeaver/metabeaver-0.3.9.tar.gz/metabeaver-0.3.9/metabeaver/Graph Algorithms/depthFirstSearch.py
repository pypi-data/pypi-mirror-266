# Depth first search, iterating through lefternmost nodes first.
# Assumes a binary tree structure, where .left and .right correspond to linked objects with a .value comparable object.
def dfs(root, target):

    # Return None if we parent node is a leaf (terminating) node, or root is actually None
    if root is None:
        return None
    # If our node has the target value in the root, return the entire node.
    if root.value == target:
        return root

    # Recurse through the left primarily and return the first lefternmost node matching target.
    left = dfs(root.left, target)
    if left is not None:
        # If we found a value traversing left, return it
        return left

    # If we searched through the leftern tree(s) and did not find the target, search right tree(s)
    right = dfs(root.right, target)
    # Will return None is entire left tree and right tree found no value, eventually returning None from root is None.
    return right