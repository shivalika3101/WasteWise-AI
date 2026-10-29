import fastapi as _fastapi
import sqlalchemy as _sa
import sqlalchemy.exc as _sa_exc

import app.dependencies as _dependencies
import app.models as _models
import app.routers.predictions as _predictions
import app.schemas as _schemas

router = _fastapi.APIRouter(prefix="/admin", tags=["admin"])


def _user_or_404(db: _dependencies.Session, user_id: int) -> _models.User:
    user = db.get(_models.User, user_id)
    if user is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def _bin_or_404(db: _dependencies.Session, bin_id: int) -> _models.Bin:
    bin_record = db.get(_models.Bin, bin_id)
    if bin_record is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="Bin not found",
        )
    return bin_record


def _instruction_or_404(db: _dependencies.Session, instruction_id: int) -> _models.DisposalInstruction:
    instruction = db.get(_models.DisposalInstruction, instruction_id)
    if instruction is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="Disposal instruction not found",
        )
    return instruction


def _category_bin_or_404(db: _dependencies.Session, mapping_id: int) -> _models.CategoryBin:
    mapping = db.get(_models.CategoryBin, mapping_id)
    if mapping is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="Mapping not found",
        )
    return mapping


def _has_conflicting_primary(db: _dependencies.Session, category_id: int, exclude_mapping_id: int | None = None) -> bool:
    statement = (
        _sa.select(_sa.func.count())
        .select_from(_models.CategoryBin)
        .where(_models.CategoryBin.category_id == category_id, _models.CategoryBin.is_primary.is_(True))
    )
    if exclude_mapping_id is not None:
        statement = statement.where(_models.CategoryBin.id != exclude_mapping_id)
    return bool(db.scalar(statement))


@router.get("/users", response_model=list[_schemas.AdminUserRead])
def list_users(admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return db.scalars(_sa.select(_models.User).order_by(_models.User.id)).all()


@router.get("/users/{user_id}", response_model=_schemas.AdminUserRead)
def get_user(user_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return _user_or_404(db, user_id)


@router.get("/users/{user_id}/predictions", response_model=list[_schemas.PredictionHistoryRead])
def user_predictions(
    user_id: int,
    admin: _dependencies.AdminUser,
    db: _dependencies.Session,
    limit: int = _fastapi.Query(default=_predictions._HISTORY_DEFAULT_LIMIT, ge=1, le=_predictions._HISTORY_MAX_LIMIT),
    offset: int = _fastapi.Query(default=0, ge=0),
):
    del admin
    _user_or_404(db, user_id)
    statement = _predictions._history_statement(user_id).limit(limit).offset(offset)
    rows = db.execute(statement).mappings()
    return [_predictions._history_read_from(row) for row in rows]


@router.post("/users/{user_id}/deactivate", response_model=_schemas.AdminUserRead)
def deactivate_user(user_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    user = _user_or_404(db, user_id)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reactivate", response_model=_schemas.AdminUserRead)
def reactivate_user(user_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    user = _user_or_404(db, user_id)
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.get("/bins", response_model=list[_schemas.AdminBinRead])
def list_bins(admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return db.scalars(_sa.select(_models.Bin).order_by(_models.Bin.name)).all()


@router.post("/bins", response_model=_schemas.AdminBinRead, status_code=_fastapi.status.HTTP_201_CREATED)
def create_bin(payload: _schemas.BinCreate, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    bin_record = _models.Bin(name=payload.name, colour=payload.colour, description=payload.description)
    db.add(bin_record)
    try:
        db.commit()
    except _sa_exc.IntegrityError:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="A bin with this name already exists",
        )
    db.refresh(bin_record)
    return bin_record


@router.patch("/bins/{bin_id}", response_model=_schemas.AdminBinRead)
def update_bin(bin_id: int, payload: _schemas.BinUpdate, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    bin_record = _bin_or_404(db, bin_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bin_record, field, value)
    try:
        db.commit()
    except _sa_exc.IntegrityError:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="A bin with this name already exists",
        )
    db.refresh(bin_record)
    return bin_record


@router.post("/bins/{bin_id}/deactivate", response_model=_schemas.AdminBinRead)
def deactivate_bin(bin_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    bin_record = _bin_or_404(db, bin_id)
    is_a_primary_bin = db.scalar(
        _sa.select(_sa.func.count())
        .select_from(_models.CategoryBin)
        .where(_models.CategoryBin.bin_id == bin_id, _models.CategoryBin.is_primary.is_(True))
    )
    if is_a_primary_bin:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="Bin is the primary bin for a category; reassign the primary bin before deactivating",
        )
    bin_record.is_active = False
    db.commit()
    db.refresh(bin_record)
    return bin_record


@router.post("/bins/{bin_id}/reactivate", response_model=_schemas.AdminBinRead)
def reactivate_bin(bin_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    bin_record = _bin_or_404(db, bin_id)
    bin_record.is_active = True
    db.commit()
    db.refresh(bin_record)
    return bin_record


@router.delete("/bins/{bin_id}", status_code=_fastapi.status.HTTP_204_NO_CONTENT)
def delete_bin(bin_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    bin_record = _bin_or_404(db, bin_id)
    referenced = (
        db.scalar(
            _sa.select(_sa.func.count()).select_from(_models.CategoryBin).where(_models.CategoryBin.bin_id == bin_id)
        )
        or db.scalar(
            _sa.select(_sa.func.count()).select_from(_models.Prediction).where(_models.Prediction.chosen_bin_id == bin_id)
        )
        or db.scalar(
            _sa.select(_sa.func.count())
            .select_from(_models.BinExamination)
            .where(_models.BinExamination.selected_bin_id == bin_id)
        )
    )
    if referenced:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="Bin is referenced by existing mappings, predictions, or bin examinations; deactivate it instead",
        )
    db.delete(bin_record)
    db.commit()
    return None


@router.get("/disposal-instructions", response_model=list[_schemas.AdminDisposalInstructionRead])
def list_disposal_instructions(admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return db.scalars(_sa.select(_models.DisposalInstruction).order_by(_models.DisposalInstruction.id)).all()


@router.post(
    "/disposal-instructions",
    response_model=_schemas.AdminDisposalInstructionRead,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def create_disposal_instruction(
    payload: _schemas.DisposalInstructionCreate, admin: _dependencies.AdminUser, db: _dependencies.Session
):
    del admin
    category = db.get(_models.Category, payload.category_id)
    if category is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )
    instruction = _models.DisposalInstruction(
        category_id=payload.category_id, instructions=payload.instructions, notes=payload.notes
    )
    db.add(instruction)
    db.commit()
    db.refresh(instruction)
    return instruction


@router.patch("/disposal-instructions/{instruction_id}", response_model=_schemas.AdminDisposalInstructionRead)
def update_disposal_instruction(
    instruction_id: int,
    payload: _schemas.DisposalInstructionUpdate,
    admin: _dependencies.AdminUser,
    db: _dependencies.Session,
):
    del admin
    instruction = _instruction_or_404(db, instruction_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(instruction, field, value)
    db.commit()
    db.refresh(instruction)
    return instruction


@router.post("/disposal-instructions/{instruction_id}/deactivate", response_model=_schemas.AdminDisposalInstructionRead)
def deactivate_disposal_instruction(instruction_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    instruction = _instruction_or_404(db, instruction_id)
    instruction.is_active = False
    db.commit()
    db.refresh(instruction)
    return instruction


@router.post("/disposal-instructions/{instruction_id}/reactivate", response_model=_schemas.AdminDisposalInstructionRead)
def reactivate_disposal_instruction(instruction_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    instruction = _instruction_or_404(db, instruction_id)
    instruction.is_active = True
    db.commit()
    db.refresh(instruction)
    return instruction


@router.get("/categories", response_model=list[_schemas.AdminCategoryRead])
def list_categories(admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return db.scalars(_sa.select(_models.Category).order_by(_models.Category.name)).all()


@router.get("/category-bins", response_model=list[_schemas.AdminCategoryBinRead])
def list_category_bins(admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    return db.scalars(_sa.select(_models.CategoryBin).order_by(_models.CategoryBin.category_id)).all()


@router.post(
    "/category-bins",
    response_model=_schemas.AdminCategoryBinRead,
    status_code=_fastapi.status.HTTP_201_CREATED,
)
def create_category_bin(
    payload: _schemas.CategoryBinCreate, admin: _dependencies.AdminUser, db: _dependencies.Session
):
    del admin
    if db.get(_models.Category, payload.category_id) is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )
    if db.get(_models.Bin, payload.bin_id) is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Bin not found",
        )
    if payload.is_primary and _has_conflicting_primary(db, payload.category_id):
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="Category already has a primary bin; unset it first",
        )
    mapping = _models.CategoryBin(
        category_id=payload.category_id, bin_id=payload.bin_id, is_primary=payload.is_primary
    )
    db.add(mapping)
    try:
        db.commit()
    except _sa_exc.IntegrityError:
        db.rollback()
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="This category is already mapped to this bin",
        )
    db.refresh(mapping)
    return mapping


@router.patch("/category-bins/{mapping_id}", response_model=_schemas.AdminCategoryBinRead)
def update_category_bin(
    mapping_id: int,
    payload: _schemas.CategoryBinUpdate,
    admin: _dependencies.AdminUser,
    db: _dependencies.Session,
):
    del admin
    mapping = _category_bin_or_404(db, mapping_id)
    if payload.is_primary and _has_conflicting_primary(db, mapping.category_id, exclude_mapping_id=mapping_id):
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_409_CONFLICT,
            detail="Category already has a primary bin; unset it first",
        )
    mapping.is_primary = payload.is_primary
    db.commit()
    db.refresh(mapping)
    return mapping


@router.delete("/category-bins/{mapping_id}", status_code=_fastapi.status.HTTP_204_NO_CONTENT)
def delete_category_bin(mapping_id: int, admin: _dependencies.AdminUser, db: _dependencies.Session):
    del admin
    mapping = _category_bin_or_404(db, mapping_id)
    db.delete(mapping)
    db.commit()
    return None
