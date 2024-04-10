from pathlib import Path

import pytest
from gentest.exec import path_to_slug, validate_query_results
from relationalai.clients import config as cfg

test_case_dir = Path(__file__).parent / "test_cases"
test_case_files = [path for path in test_case_dir.iterdir() if path.suffix == ".py"]

# This test absorbs the latency of the engine being created
def test_engine_creation_dummy(engine_config: cfg.Config):
    pass

@pytest.mark.parametrize("file_path", test_case_files, ids=lambda path: path_to_slug(path, test_case_dir))
def test_snapshots(file_path: Path, snapshot, engine_config: cfg.Config):
    validate_query_results(file_path, snapshot, {"test_config": engine_config})
