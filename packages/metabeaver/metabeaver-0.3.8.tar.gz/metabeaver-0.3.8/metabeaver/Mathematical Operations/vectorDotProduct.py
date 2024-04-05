from math import sqrt


# Calculates the dot product of two vectors; divides the product of element pairs by the product of vector magnitude.
def vectorDotProduct(vectorOne, vectorTwo):

    # For a given vector, sum the absolute magnitude.
    def getVectorMagnitude(vector):

        squareTotal = 0
        for eachDirection in vector:
            squareTotal = squareTotal + eachDirection * eachDirection

        vectorMagnitude = sqrt(squareTotal)
        return vectorMagnitude

    # Get the sum of the multiplication of pairwise vector elements.
    dotTotal = 0
    for i in range(len(vectorOne)):
        dotTotal = dotTotal + vectorOne[i] * vectorTwo[i]

    # Divide the product of vector pairs by the product of the vector magnitudes
    vectorDotProduct = dotTotal / getVectorMagnitude(vectorOne) * getVectorMagnitude(vectorTwo)

    # Returns a range of -1 to 1, including zero; -1 is opposite direction, 0 is orthogonal, 1 is completely similar
    return vectorDotProduct




























