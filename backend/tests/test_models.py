import sqlalchemy as _sa
import app.database as _database
import app.models as _models


def test_all_tables_are_registered():
    assert set(_database.Base.metadata.tables) == {
        "categories",
        "bins",
        "category_bins",
        "disposal_instructions",
        "predictions",
        "users",
        "bin_examinations",
        "blog_posts",
    }


def test_category_columns_match_the_schema():
    columns = _models.Category.__table__.columns
    assert columns["name"].type.length == 50
    assert columns["name"].unique
    assert not columns["name"].nullable
    assert columns["display_name"].nullable
    assert columns["model_label_index"].unique
    assert not columns["created_at"].nullable


def test_bin_lifecycle_columns_match_the_schema():
    columns = _models.Bin.__table__.columns
    assert not columns["is_active"].nullable
    assert isinstance(columns["is_active"].type, _sa.Boolean)
    assert not columns["created_at"].nullable
    assert not columns["updated_at"].nullable


def test_disposal_instruction_lifecycle_columns_match_the_schema():
    columns = _models.DisposalInstruction.__table__.columns
    assert not columns["is_active"].nullable
    assert isinstance(columns["is_active"].type, _sa.Boolean)
    assert not columns["created_at"].nullable
    assert not columns["updated_at"].nullable


def test_category_bin_timestamp_columns_match_the_schema():
    columns = _models.CategoryBin.__table__.columns
    assert not columns["created_at"].nullable
    assert not columns["updated_at"].nullable


def test_category_bins_constraints_are_named():
    names = {constraint.name for constraint in _models.CategoryBin.__table__.constraints}
    assert {"unique_category_bin", "fk_category", "fk_bin"} <= names


def test_category_bins_cascade_on_delete():
    for column in ("category_id", "bin_id"):
        foreign_key = next(iter(_models.CategoryBin.__table__.columns[column].foreign_keys))
        assert foreign_key.ondelete == "CASCADE"


def test_disposal_instructions_cascade_on_delete():
    columns = _models.DisposalInstruction.__table__.columns
    assert next(iter(columns["category_id"].foreign_keys)).ondelete == "CASCADE"
    assert not columns["instructions"].nullable
    assert columns["notes"].nullable


def test_predictions_keep_history_when_references_are_deleted():
    columns = _models.Prediction.__table__.columns
    assert columns["predicted_category_id"].nullable
    assert columns["chosen_bin_id"].nullable
    assert columns["is_correct"].nullable
    assert next(iter(columns["predicted_category_id"].foreign_keys)).ondelete is None
    assert next(iter(columns["chosen_bin_id"].foreign_keys)).ondelete is None


def test_prediction_confidence_precision():
    confidence = _models.Prediction.__table__.columns["confidence"].type
    assert isinstance(confidence, _sa.Numeric)
    assert (confidence.precision, confidence.scale) == (5, 4)


def test_predictions_created_at_is_indexed():
    assert {index.name for index in _models.Prediction.__table__.indexes} == {"ix_predictions_created_at",
        "ix_predictions_user_id",}

def test_user_columns_match_the_schema():
    columns = _models.User.__table__.columns
    assert columns["email"].unique
    assert not columns["email"].nullable
    assert not columns["password_hash"].nullable
    assert "password" not in _models.User.__table__.columns
    assert not columns["created_at"].nullable

def test_user_role_defaults_to_user():
    role = _models.User.__table__.columns["role"]
    assert not role.nullable
    assert role.server_default.arg == "user"

def test_user_is_active_defaults_to_true():
    is_active = _models.User.__table__.columns["is_active"]
    assert not is_active.nullable
    assert isinstance(is_active.type, _sa.Boolean)

def test_prediction_user_id_is_nullable_and_indexed_foreign_key():
    columns = _models.Prediction.__table__.columns
    assert columns["user_id"].nullable
    foreign_key = next(iter(columns["user_id"].foreign_keys))
    assert foreign_key.target_fullname == "users.id"
    assert foreign_key.constraint.name == "fk_prediction_user"

def test_user_predictions_relationship_is_bidirectional():
    assert _models.User.predictions.property.mapper.class_ is _models.Prediction
    assert _models.Prediction.user.property.mapper.class_ is _models.User

def test_bin_examination_cascades_on_prediction_delete():
    columns = _models.BinExamination.__table__.columns
    assert next(iter(columns["prediction_id"].foreign_keys)).ondelete == "CASCADE"
    assert not columns["selected_bin_id"].nullable
    assert not columns["is_correct"].nullable

def test_bin_examination_prediction_id_is_indexed():
    assert {index.name for index in _models.BinExamination.__table__.indexes} == {"ix_bin_examinations_prediction_id"}


def test_blog_post_columns_match_the_schema():
    columns = _models.BlogPost.__table__.columns
    assert columns["slug"].unique
    assert not columns["slug"].nullable
    assert not columns["title"].nullable
    assert not columns["summary"].nullable
    assert not columns["body"].nullable
    assert not columns["status"].nullable
