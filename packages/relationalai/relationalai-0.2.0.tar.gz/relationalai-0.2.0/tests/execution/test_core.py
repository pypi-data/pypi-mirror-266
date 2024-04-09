from pathlib import Path
import pytest
from gentest.exec import validate_query_results, path_to_slug

basic_dir = Path(__file__).parent / "basic"
basic_files = [path for path in basic_dir.iterdir() if path.suffix == ".py"]

@pytest.mark.parametrize("file_path", basic_files, ids=lambda path: path_to_slug(path, basic_dir))
def test_basic(file_path: Path, snapshot):
    validate_query_results(file_path, snapshot)
