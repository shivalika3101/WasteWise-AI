import pathlib as _pathlib
import alembic.config as _alembic_config
import alembic.script as _alembic_script
import app.database as _database


def script_directory():
    config = _alembic_config.Config(str(_pathlib.Path(__file__).resolve().parent.parent / "alembic.ini"))
    return _alembic_script.ScriptDirectory.from_config(config)


def test_there_is_exactly_one_head():
    assert len(script_directory().get_heads()) == 1


def test_the_baseline_has_no_parent():
    revisions = list(script_directory().walk_revisions())
    assert revisions[-1].down_revision is None


def test_every_model_table_is_covered_by_a_migration():
    source = "".join(
        revision.module.__file__ and _pathlib.Path(revision.module.__file__).read_text()
        for revision in script_directory().walk_revisions()
    )
    for table in _database.Base.metadata.tables:
        assert f"'{table}'" in source
