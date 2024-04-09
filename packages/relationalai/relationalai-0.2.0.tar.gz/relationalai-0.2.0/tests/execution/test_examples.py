from pathlib import Path
import pytest
from gentest.util import PROJECT_DIR
from gentest.exec import validate_query_results, path_to_slug

example_dir = Path(PROJECT_DIR) / "examples"
example_files = [path for path in example_dir.iterdir() if path.suffix == ".py"]

@pytest.mark.parametrize("file_path", example_files, ids=lambda path: path_to_slug(path, example_dir))
def test_example(file_path: Path, snapshot):
    validate_query_results(file_path, snapshot)
