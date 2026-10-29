import unittest.mock as _mock
import pytest as _pytest
import app.bootstrap as _bootstrap


def configured_inspector(*, users: bool, user_id: bool, user_index: bool, user_foreign_key: bool):
    inspector = _mock.MagicMock()
    tables = ["categories", "bins", "category_bins", "disposal_instructions", "predictions"]
    if users:
        tables.append("users")
    inspector.get_table_names.return_value = tables
    inspector.get_columns.return_value = [{"name": "user_id"}] if user_id else []
    inspector.get_indexes.return_value = [
        {"name": "ix_predictions_created_at"},
        *([{"name": "ix_predictions_user_id"}] if user_index else []),
    ]
    inspector.get_foreign_keys.return_value = [{"name": "fk_prediction_user"}] if user_foreign_key else []
    return inspector


def test_unmanaged_database_already_at_head_matches_head_revision():
    config = _bootstrap.alembic_config()
    fake_engine = _mock.MagicMock()
    with _mock.patch("sqlalchemy.inspect") as inspect:
        inspect.return_value = configured_inspector(
            users=True, user_id=True, user_index=True, user_foreign_key=True
        )
        assert _bootstrap.matching_revision(fake_engine, config) == "fe721af44f4a"


def test_unmanaged_database_at_baseline_matches_baseline_revision():
    config = _bootstrap.alembic_config()
    fake_engine = _mock.MagicMock()
    with _mock.patch("sqlalchemy.inspect") as inspect:
        inspect.return_value = configured_inspector(
            users=False, user_id=False, user_index=False, user_foreign_key=False
        )
        assert _bootstrap.matching_revision(fake_engine, config) == _bootstrap.base_revision(config)


def test_partially_applied_revision_is_rejected():
    config = _bootstrap.alembic_config()
    fake_engine = _mock.MagicMock()
    with _mock.patch("sqlalchemy.inspect") as inspect:
        inspect.return_value = configured_inspector(
            users=True, user_id=False, user_index=False, user_foreign_key=False
        )
        with _pytest.raises(RuntimeError, match="partially matches"):
            _bootstrap.matching_revision(fake_engine, config)
