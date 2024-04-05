import numpy as np


def lasso_regression(X, y, learning_rate, regularization, num_iterations):
    """
    Perform Lasso Regression using gradient descent.

    Parameters:
    -----------
    X : numpy.ndarray
        Feature matrix with shape (m, n)
            m is the number of samples
            n is the number of features
                Can be thought of as rows and columns.

    y : numpy.ndarray
        Target vector with shape (m,).

    learning_rate : float
        The step size used in gradient descent to update the weights.

    regularization : float
        Regularization parameter (lambda) controlling the strength of the L1 regularization term.

    num_iterations : int
        The number of iterations for gradient descent.

    Returns:
    --------
    numpy.ndarray
        Final weights after Lasso Regression.

    Example:
    ---------
    # Example usage with synthetic data
    X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    y = np.array([10, 20, 30])

    # Hyperparameters
    learning_rate = 0.01
    regularization = 0.5
    num_iterations = 1000

    # Call lasso_regression function
    weights = lasso_regression(X, y, learning_rate, regularization, num_iterations)

    # Print the final weights
    print("Final Weights:", weights)
    """

    # Initialize weights
    weights = np.ones(X.shape[1])

    # Iteratively update the weights
    for iteration in range(num_iterations):

        # Make predictions
        predictions = np.dot(X, weights)

        # Calculate residuals
        residuals = predictions - y

        # Update weights using gradient descent with L1 regularization
        gradient = np.dot(X.T, residuals) / len(y)
        weights = weights - learning_rate * (gradient + regularization * np.sign(weights))

    return weights

# Test Example:
# This example demonstrates how to use the function with synthetic data.

# Generate synthetic data
X_test = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
y_test = np.array([10, 20, 30])

# Hyperparameters for testing
learning_rate_test = 0.01
regularization_test = 0.5
num_iterations_test = 1000

# Call lasso_regression function
weights_test = lasso_regression(X_test, y_test, learning_rate_test, regularization_test, num_iterations_test)

# Print the final weights for the test example
print("Test Example - Final Weights:", weights_test)

# Using the weights obtained from the lasso regression
final_weights = weights_test  # Replace with the actual weights obtained from the lasso regression

# Example data for fitting
X_fit = np.array([[2, 3, 4], [5, 6, 7], [8, 9, 10]])

# Make predictions using the final weights
predictions_fit = np.dot(X_fit, final_weights)

# Print the predictions
print("Predictions on Fitting Data:", predictions_fit)

























