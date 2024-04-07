def generate_subsets(nums):

    """
    Generates all subsets of a given list of distinct integers.

    Args:
        nums (List[int]): A list of distinct integers.

    Returns:
        List[List[int]]: A list of all possible subsets of the input list.

    If we had a basket of 4 different mushrooms, here are all the different recipes we could follow:
    0000   No mushrooms
    0001         🍄
    0010       🍄
    0011       🍄🍄
    0100     🍄
    0101     🍄  🍄
    0110     🍄🍄
    0111     🍄🍄🍄
    1000   🍄
    1001   🍄  🍄
    1010   🍄  🍄
    1011   🍄  🍄🍄
    1100   🍄🍄
    1101   🍄🍄  🍄
    1110   🍄🍄🍄
    1111   🍄🍄🍄🍄


    """

    # Initialize an empty list to store subsets
    subsets = []

    # Get the length of the input list
    n = len(nums)

    # Use binary numbers to represent subsets
    # Note cardinality of the set of all sets, the total number of subsets, is 2^n.
    for i in range(2 ** n):
        # Initialize an empty subset for the current binary number
        subset = []

        # Iterate through the bits of the binary number. Note j is the length of the number of elements in our set.
        # For a set with 4 elements, 16 possible combinations - 0000 to 1111. j indexes into the nth element.
        # Total binary digits is 2 ** n (the binary numbers) * n iterations (the positions, represented by j).
        for j in range(n):
            # Check if the jth bit is set(1) in the binary number.
            # Consider i to be the index of the current iteration, *in binary*. e.g. 0000, 0001, 0010 ... 1110, 1111.
            # We will now add all elements to the subset list where there's a 1 in the binary string.
            if (i >> j) & 1:
                # Add the corresponding element to the subset
                subset.append(nums[j])

        # Add the subset to the list of subsets
        subsets.append(subset)

    # Return the list of all generated subsets
    return subsets


nums = [1, 2, 3, 4]
test = generate_subsets(nums)
print(test)

"""

### Explanation for different values of j ###

# Note this adds sets IN REVERSE ORDER, EXCEPT for 0000 and 1111.
# WHY? Because we FIRST check whether elements on the RIGHT are 0 or 1. 
# We then move across the binary number, going LEFT.
# BUT for 0000 ALL elements are zero, so we never add anything.
# BUT for 1111 ALL elements are one, so we add EVERYTHING.
# To add in a more intuitive fashion, you can use the LEFT SHIFT OPERATOR, <<, which startS at index 0 and moves RIGHT.

# Example: 0001 - adds 1000 to the subset
# - i is the integer 1 in binary.
# - When j is 0:
#   - (i >> j) is 0001, and (i >> j) & 1 is 1, indicating that the rightmost bit of 0001 is 1.
# - When j is 1:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the second rightmost bit of 0001 is 0.
# - When j is 2:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the third rightmost bit of 0001 is 0.
# - When j is 3:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the fourth rightmost bit of 0001 is 0.

# Example: 0010 - adds 0100 to the subset 
# - i is 2 in binary.
# - When j is 0:
#   - (i >> j) is 0010, and (i >> j) & 1 is 0, indicating that the rightmost bit of 0010 is 0.
# - When j is 1:
#   - (i >> j) is 0001, and (i >> j) & 1 is 1, indicating that the second rightmost bit of 0010 is 1.
# - When j is 2:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the third rightmost bit of 0010 is 0.
# - When j is 3:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the fourth rightmost bit of 0010 is 0.

# Example: 0101 - adds 1010 to the subset
# - i is 0101 in binary.
# - When j is 0:
#   - (i >> j) is 0101, and (i >> j) & 1 is 1, indicating that the rightmost bit of 0101 is 1.
# - When j is 1:
#   - (i >> j) is 0010, and (i >> j) & 1 is 0, indicating that the second rightmost bit of 0101 is 0.
# - When j is 2:
#   - (i >> j) is 0001, and (i >> j) & 1 is 1, indicating that the third rightmost bit of 0101 is 1.
# - When j is 3:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that the fourth rightmost bit of 0101 is 0.

# Example: 1110 - adds 0111 to the subset
# - i is 1110 in binary.
# - When j is 0:
#   - (i >> j) is 1110, and (i >> j) & 1 is 0, indicating that the rightmost bit of 1110 is 0.
# - When j is 1:
#   - (i >> j) is 0111, and (i >> j) & 1 is 1, indicating that the second rightmost bit of 1110 is 1.
# - When j is 2:
#   - (i >> j) is 0011, and (i >> j) & 1 is 1, indicating that the third rightmost bit of 1110 is 1.
# - When j is 3:
#   - (i >> j) is 0001, and (i >> j) & 1 is 1, indicating that the fourth rightmost bit of 1110 is 1.

# Example: 1111
# - i is 1111 in binary.
# - When j is 0:
#   - (i >> j) is 1111, and (i >> j) & 1 is 1, indicating that the rightmost bit of 1111 is 1.
# - When j is 1:
#   - (i >> j) is 0111, and (i >> j) & 1 is 1, indicating that the second rightmost bit of 1111 is 1.
# - When j is 2:
#   - (i >> j) is 0011, and (i >> j) & 1 is 1, indicating that the third rightmost bit of 1111 is 1.
# - When j is 3:
#   - (i >> j) is 0001, and (i >> j) & 1 is 1, indicating that the fourth rightmost bit of 1111 is 1.
# - When j is 4:
#   - (i >> j) is 0000, and (i >> j) & 1 is 0, indicating that there is no fifth rightmost bit.


"""