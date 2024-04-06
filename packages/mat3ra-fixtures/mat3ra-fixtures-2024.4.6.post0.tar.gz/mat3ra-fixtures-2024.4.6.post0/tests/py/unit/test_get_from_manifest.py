from pathlib import Path

from mat3ra.fixtures import get_content_by_reference_path

PATH_IN_MANIFEST = "applications/espresso/v5.4.0/stdin"
PATH_IN_FILESYSTEM = "data/applications/espresso/5.4.0/case-001/pw-scf.in"


def test_get_content_by_reference_path():
    content = get_content_by_reference_path(PATH_IN_MANIFEST)
    original = open(Path(__file__).parents[3] / PATH_IN_FILESYSTEM).read()
    assert content == original
