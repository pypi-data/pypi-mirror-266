import math


# Calculates the logarithmic value of a number in base two, then adds one for number of bits needed in binary
def binaryPlaces(placeNum):

    # Get the log of the integer in base two
    places = int(math.log(abs(placeNum), 2))

    # Add one to extend to the ceiling, e.g. 12 --> approx 3.5 --> 4
    places = int(places) + 1

    return places


# Reverses a binary representation of a number.
def reverseBinary(binary_num):

    # Initialize the inverted_num variable to store the result
    inverted_num = 0

    # Iterate through each bit in the binary representation of the number
    for i in range(len(binary_num)):

        # Calculate the value of the current bit (1 or 0) using a bitwise AND operation
        current_bit = (1 << i) & 1
        print(current_bit)

        # Shift the current bit to its correct position in the inverted number
        # The bit position is determined by the difference between the total number of bits
        # and the current iteration index minus one (to account for zero-based indexing)
        inverted_bit_position = len(binary_num) - i - 1

        # Update the inverted_num using a bitwise OR operation to set the bit at the calculated position
        inverted_num |= (current_bit << inverted_bit_position)

    return inverted_num


def twos_complement(num):

    """
    Calculate the two's complement of an integer.

    Args:
        num (int): The integer for which the two's complement should be calculated.

    Returns:
        str: The binary representation of the two's complement.

    Example:
        #>>> twos_complement(5)
        '0101'  # Positive number in 4-bit representation
        #>>> twos_complement(-5)
        '1011'  # Two's complement of a negative number in 4-bit representation
    """

    # Get number of binary places to use, given length of our integer
    maxBin = binaryPlaces(num)

    # Check if num is positive
    if num >= 0:
        binary_num = bin(num)[2:]
        return binary_num.zfill(maxBin)  # Use 4-bit representation

    # For positive numbers, just convert to binary and pad with zeros if needed
    if num < 0:
        # Calculate the absolute value of num
        num = abs(num)

        # Convert num to binary and remove the '0b' prefix
        binary_num = bin(num)[2:]

        # Ensure the binary representation has enough bits
        binary_num = binary_num.zfill(maxBin)  # Use minimal bit representation
        print(binary_num)

        # Invert (flip) all the bits
        inverted_num = reverseBinary(binary_num)
        print(inverted_num)

        # Add 1 to the inverted binary representation
        result = inverted_num[-1] = 1

        #result = bin(int(inverted_num, len(inverted_num)) + 1)
        print(result)

        return result  # Return the binary result


convertedNum = twos_complement(-5)
print(convertedNum)


# Convert decimal 5 to binary and reverse it
decimal_num = 6
binary_representation = bin(decimal_num)[2:]
reversed_binary = bin(reverseBinary(binary_representation))[2:]
print(reversed_binary)  # Output: 6