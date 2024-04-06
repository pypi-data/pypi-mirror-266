from contextlib import contextmanager
from pathlib import Path

from .models import Setups


@contextmanager
def setup_db(db_file: Path):
    try:
        if db_file.exists():
            if not db_file.is_file():
                raise RuntimeError(f"{db_file} is not a file")
            setups = Setups.model_validate_json(db_file.read_text())
        else:
            setups = Setups(setups=[])
        yield setups
    finally:
        db_file.parent.mkdir(exist_ok=True, parents=True)
        db_file.write_text(setups.model_dump_json())
