import datetime as _datetime
import typing as _typing
import pydantic as _pydantic

_BCRYPT_MAX_PASSWORD_BYTES = 72

NormalisedEmail = _typing.Annotated[_pydantic.EmailStr, _pydantic.AfterValidator(str.lower)]


class UserCreate(_pydantic.BaseModel):
    email: NormalisedEmail
    password: str = _pydantic.Field(min_length=8)

    @_pydantic.field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode()) > _BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(f"password must be at most {_BCRYPT_MAX_PASSWORD_BYTES} bytes")
        return value


class UserLogin(_pydantic.BaseModel):
    email: NormalisedEmail
    password: str


class UserRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    email: _pydantic.EmailStr
    role: str
    created_at: _datetime.datetime


class AdminUserRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    email: _pydantic.EmailStr
    role: str
    is_active: bool
    created_at: _datetime.datetime


class Token(_pydantic.BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionRead(_pydantic.BaseModel):
    prediction_id: int
    category: str
    confidence: float = _pydantic.Field(ge=0, le=1)
    bin: str
    guidance: str


class PredictionHistoryRead(_pydantic.BaseModel):
    """A completed prediction, with no image or account data exposed."""

    prediction_id: int
    category: str
    confidence: float = _pydantic.Field(ge=0, le=1)
    bin: str
    guidance: str
    created_at: _datetime.datetime


class ProfileSummary(_pydantic.BaseModel):
    total_predictions: int
    latest_prediction: PredictionHistoryRead | None
    most_frequent_category: str | None


class BinExaminationCreate(_pydantic.BaseModel):
    selected_bin_id: int


class BinExaminationRead(_pydantic.BaseModel):
    selected_bin: str
    is_correct: bool
    recommended_bin: str
    guidance: str


class BinOptionRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class BinCreate(_pydantic.BaseModel):
    name: str = _pydantic.Field(min_length=1, max_length=50)
    colour: str | None = _pydantic.Field(default=None, max_length=20)
    description: str | None = None


class BinUpdate(_pydantic.BaseModel):
    name: str | None = _pydantic.Field(default=None, min_length=1, max_length=50)
    colour: str | None = _pydantic.Field(default=None, max_length=20)
    description: str | None = None


class AdminBinRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    colour: str | None
    description: str | None
    is_active: bool
    created_at: _datetime.datetime
    updated_at: _datetime.datetime


class DisposalInstructionCreate(_pydantic.BaseModel):
    category_id: int
    instructions: str = _pydantic.Field(min_length=1)
    notes: str | None = None


class DisposalInstructionUpdate(_pydantic.BaseModel):
    instructions: str | None = _pydantic.Field(default=None, min_length=1)
    notes: str | None = None


class AdminDisposalInstructionRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    category_id: int
    instructions: str
    notes: str | None
    is_active: bool
    created_at: _datetime.datetime
    updated_at: _datetime.datetime


class AdminCategoryRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    display_name: str | None
    model_label_index: int


class CategoryBinCreate(_pydantic.BaseModel):
    category_id: int
    bin_id: int
    is_primary: bool = False


class CategoryBinUpdate(_pydantic.BaseModel):
    is_primary: bool


class AdminCategoryBinRead(_pydantic.BaseModel):
    model_config = _pydantic.ConfigDict(from_attributes=True)

    id: int
    category_id: int
    bin_id: int
    is_primary: bool
    created_at: _datetime.datetime
    updated_at: _datetime.datetime


class BlogPostSummary(_pydantic.BaseModel):
    slug: str
    title: str
    summary: str
    created_at: _datetime.datetime


class BlogPostRead(_pydantic.BaseModel):
    slug: str
    title: str
    summary: str
    body: str
    created_at: _datetime.datetime
