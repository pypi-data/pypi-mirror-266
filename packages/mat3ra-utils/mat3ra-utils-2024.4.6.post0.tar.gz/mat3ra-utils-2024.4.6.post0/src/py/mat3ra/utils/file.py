import os


def get_file_content(file_path: str) -> str:
    """
    Returns the content of a given file.

    Args:
        file_path (str): file path.

    Returns:
         str
    """
    content = ""
    if file_path and os.path.exists(file_path):
        with open(file_path) as f:
            content = f.read()
    return content
