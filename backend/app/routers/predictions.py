import decimal as _decimal
import io as _io

import fastapi as _fastapi
import PIL as _pil
import PIL.Image as _image
import sqlalchemy as _sa
import sqlalchemy.exc as _sa_exc

import app.dependencies as _dependencies
import app.models as _models
import app.predictor as _predictor
import app.schemas as _schemas

MAX_IMAGE_BYTES = 5 * 1024 * 1024
_SUPPORTED_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
}

router = _fastapi.APIRouter(
    prefix="/predictions",
    tags=["predictions"],
)


_HISTORY_DEFAULT_LIMIT = 20
_HISTORY_MAX_LIMIT = 100

# The database keeps the legacy guidance names, while the Cardiff UI presents
# the physical containers residents use.  Both legacy recycling categories go
# into the same red sack.
_LOCAL_CONTAINER_KEYS = {
    "Mixed Dry Recycling": "red-recycling-sack",
    "Plastic & Cans": "red-recycling-sack",
}


def _history_statement(user_id: int):
    return (
        _sa.select(
            _models.Prediction.id.label("prediction_id"),
            _models.Category.display_name,
            _models.Category.name,
            _models.Prediction.confidence,
            _models.Bin.name.label("bin"),
            _models.DisposalInstruction.instructions.label("guidance"),
            _models.Prediction.created_at,
        )
        .join(_models.Category, _models.Category.id == _models.Prediction.predicted_category_id)
        .join(_models.Bin, _models.Bin.id == _models.Prediction.chosen_bin_id)
        .join(
            _models.DisposalInstruction,
            _models.DisposalInstruction.category_id == _models.Category.id,
        )
        .where(_models.Prediction.user_id == user_id)
        .order_by(_models.Prediction.created_at.desc(), _models.Prediction.id.desc())
    )


def _history_read_from(row) -> _schemas.PredictionHistoryRead:
    return _schemas.PredictionHistoryRead(
        prediction_id=row["prediction_id"],
        category=row["display_name"] or row["name"],
        confidence=float(row["confidence"]),
        bin=row["bin"],
        guidance=row["guidance"],
        created_at=row["created_at"],
    )


@router.get(
    "/history",
    response_model=list[_schemas.PredictionHistoryRead],
)
def prediction_history(
    user: _dependencies.CurrentUser,
    db: _dependencies.Session,
    limit: int = _fastapi.Query(default=_HISTORY_DEFAULT_LIMIT, ge=1, le=_HISTORY_MAX_LIMIT),
    offset: int = _fastapi.Query(default=0, ge=0),
):
    """Return only the signed-in user's completed predictions, newest first."""
    statement = _history_statement(user.id).limit(limit).offset(offset)
    rows = db.execute(statement).mappings()
    return [_history_read_from(row) for row in rows]


@router.get(
    "/summary",
    response_model=_schemas.ProfileSummary,
)
def prediction_summary(
    user: _dependencies.CurrentUser,
    db: _dependencies.Session,
):
    """Return the signed-in user's prediction totals, latest result, and most frequent category."""
    total = db.scalar(
        _sa.select(_sa.func.count())
        .select_from(_models.Prediction)
        .where(_models.Prediction.user_id == user.id)
    )

    latest_row = db.execute(_history_statement(user.id).limit(1)).mappings().first()
    latest = _history_read_from(latest_row) if latest_row is not None else None

    frequent_row = db.execute(
        _sa.select(
            _sa.func.coalesce(_models.Category.display_name, _models.Category.name).label("category"),
            _sa.func.count().label("occurrences"),
            _sa.func.max(_models.Prediction.created_at).label("most_recent"),
        )
        .select_from(_models.Prediction)
        .join(_models.Category, _models.Category.id == _models.Prediction.predicted_category_id)
        .where(_models.Prediction.user_id == user.id)
        .group_by(_models.Category.id)
        .order_by(_sa.desc("occurrences"), _sa.desc("most_recent"))
        .limit(1)
    ).mappings().first()

    return _schemas.ProfileSummary(
        total_predictions=total,
        latest_prediction=latest,
        most_frequent_category=frequent_row["category"] if frequent_row is not None else None,
    )


def _read_image(image: _fastapi.UploadFile) -> bytes:
    expected_format = _SUPPORTED_TYPES.get(image.content_type or "")
    if expected_format is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG and PNG images are supported",
        )

    image_bytes = image.file.read(MAX_IMAGE_BYTES + 1)
    if not image_bytes:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image is empty",
        )
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_413_CONTENT_TOO_LARGE,
            detail="The uploaded image must be 5 MB or smaller",
        )

    try:
        with _image.open(_io.BytesIO(image_bytes)) as decoded:
            if decoded.format != expected_format:
                raise _fastapi.HTTPException(
                    status_code=_fastapi.status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="The image content does not match its file type",
                )
            decoded.verify()
    except _fastapi.HTTPException:
        raise
    except (_pil.UnidentifiedImageError, _image.DecompressionBombError, OSError) as error:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image could not be read",
        ) from error

    return image_bytes


def _primary_guidance_statement():
    return (
        _sa.select(_models.Category, _models.Bin, _models.DisposalInstruction)
        .join(_models.CategoryBin, _models.CategoryBin.category_id == _models.Category.id)
        .join(_models.Bin, _models.Bin.id == _models.CategoryBin.bin_id)
        .join(
            _models.DisposalInstruction,
            _models.DisposalInstruction.category_id == _models.Category.id,
        )
        .where(_models.CategoryBin.is_primary.is_(True))
    )


def _guidance_for(db: _dependencies.Session, label_index: int):
    statement = _primary_guidance_statement().where(_models.Category.model_label_index == label_index)
    return db.execute(statement).first()


def _guidance_for_category(db: _dependencies.Session, category_id: int | None):
    if category_id is None:
        return None
    statement = _primary_guidance_statement().where(_models.Category.id == category_id)
    return db.execute(statement).first()


def _local_container_key(bin_record: _models.Bin) -> str:
    return _LOCAL_CONTAINER_KEYS.get(bin_record.name, bin_record.name)


@router.get(
    "/bins",
    response_model=list[_schemas.BinOptionRead],
)
def available_bins(
    user: _dependencies.CurrentUser,
    db: _dependencies.Session,
):
    """Return the stable bin identifiers needed for a signed-in user's answer."""
    del user
    statement = _sa.select(_models.Bin).where(_models.Bin.is_active.is_(True)).order_by(_models.Bin.name)
    return db.scalars(statement).all()


@router.post(
    "/",
    response_model=_schemas.PredictionRead,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def predict_image(
    user: _dependencies.CurrentUser,
    db: _dependencies.Session,
    image: _fastapi.UploadFile = _fastapi.File(...),
):
    image_bytes = _read_image(image)

    try:
        prediction = _predictor.predict(image_bytes)
    except _predictor.InvalidImageError as error:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="The uploaded image could not be read",
        ) from error
    except _predictor.PredictorError as error:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The classification service is unavailable",
        ) from error

    try:
        guidance = _guidance_for(db, prediction.label_index)
        if guidance is None:
            db.rollback()
            raise _fastapi.HTTPException(
                status_code=_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No disposal guidance exists for this classification",
            )

        category, bin_record, instruction = guidance
        if category.name != prediction.label:
            db.rollback()
            raise _fastapi.HTTPException(
                status_code=_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The classification does not match the category data",
            )

        stored = _models.Prediction(
            predicted_category_id=category.id,
            confidence=_decimal.Decimal(str(prediction.confidence)),
            chosen_bin_id=bin_record.id,
            user_id=user.id,
        )
        db.add(stored)
        db.flush()
        response = _schemas.PredictionRead(
            prediction_id=stored.id,
            category=category.display_name or category.name,
            confidence=prediction.confidence,
            bin=bin_record.name,
            guidance=instruction.instructions,
        )
        db.commit()
    except _fastapi.HTTPException:
        raise
    except _sa_exc.SQLAlchemyError as error:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The prediction could not be saved",
        ) from error

    return response


@router.post(
    "/{prediction_id}/bin-examinations",
    response_model=_schemas.BinExaminationRead,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def examine_bin(
    prediction_id: int,
    payload: _schemas.BinExaminationCreate,
    user: _dependencies.CurrentUser,
    db: _dependencies.Session,
):
    prediction = db.get(_models.Prediction, prediction_id)
    if prediction is None or prediction.user_id != user.id:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    selected_bin = db.get(_models.Bin, payload.selected_bin_id)
    if selected_bin is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="The selected bin does not exist",
        )

    guidance = _guidance_for_category(db, prediction.predicted_category_id)
    if guidance is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No disposal guidance exists for this prediction's category",
        )

    _, recommended_bin, instruction = guidance
    is_correct = _local_container_key(selected_bin) == _local_container_key(recommended_bin)

    try:
        db.add(
            _models.BinExamination(
                prediction_id=prediction.id,
                selected_bin_id=selected_bin.id,
                is_correct=is_correct,
            )
        )
        db.commit()
    except _sa_exc.SQLAlchemyError as error:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The bin examination could not be saved",
        ) from error

    return _schemas.BinExaminationRead(
        selected_bin=selected_bin.name,
        is_correct=is_correct,
        recommended_bin=recommended_bin.name,
        guidance=instruction.instructions,
    )
