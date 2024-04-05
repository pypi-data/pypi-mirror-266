# Create a markdown file by passing a literal string and a filename
def create_markdown_file(content: str, filename: str) -> None:
    """
    Create a Markdown file with the given content and filename.
    Args:
        content (str): The Markdown content to be written to the file.
        filename (str): The name of the Markdown file to be created.
    """

    # Check if the filename has the correct extension
    if not filename.endswith(".md"):
        filename += ".md"
    # Create and write the content to the file
    with open(filename, "w", encoding="utf-8") as md_file:
        md_file.write(content)

    """
    Example useage:

       literalString = someLiteralStringObject
       fileName = 'codeFlow'
       create_markdown_file(literalString, fileName)    
    
    """




