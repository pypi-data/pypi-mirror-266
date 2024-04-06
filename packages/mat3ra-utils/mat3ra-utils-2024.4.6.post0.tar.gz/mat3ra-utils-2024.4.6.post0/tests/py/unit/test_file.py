from pathlib import Path

from mat3ra.utils import file as utils

REFERENCE_FILE_PATH = Path(__file__).parent / "./fixtures/file_with_content.txt"
REFERENCE_FILE_CONTENT = """Content Line 1\nContent Line 2\nContent Line 3\n"""


def test_file_get_content():
    """
    test_camel_to_snake should be converted to testCamelToSnake
    """
    content = utils.get_file_content(REFERENCE_FILE_PATH)
    assert content == REFERENCE_FILE_CONTENT
