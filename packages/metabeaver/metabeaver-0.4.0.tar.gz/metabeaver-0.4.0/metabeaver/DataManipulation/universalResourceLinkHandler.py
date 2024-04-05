from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Check if a given string can be parsed to a valid URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string can be parsed to a valid URL, False otherwise.
    """
    # Attempt to parse the input URL using urlparse
    try:
        result = urlparse(url)
        # Check if the scheme and netloc components are non-empty
        if all([result.scheme, result.netloc]):
            # If both components are non-empty, the URL is valid
            return True
        else:
            # If either component is empty, the URL is invalid
            return False
    # If urlparse raises a ValueError, the input string is not a valid URL
    except ValueError:
        return False