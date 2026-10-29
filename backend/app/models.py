import datetime as _datetime
import decimal as _decimal
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import app.database as _database


class Category(_database.Base):
    __tablename__ = "categories"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    name: _orm.Mapped[str] = _orm.mapped_column(_sa.String(50), unique=True)
    display_name: _orm.Mapped[str | None] = _orm.mapped_column(_sa.String(80))
    model_label_index: _orm.Mapped[int] = _orm.mapped_column(unique=True)
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())


class Bin(_database.Base):
    __tablename__ = "bins"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    name: _orm.Mapped[str] = _orm.mapped_column(_sa.String(50), unique=True)
    colour: _orm.Mapped[str | None] = _orm.mapped_column(_sa.String(20))
    description: _orm.Mapped[str | None] = _orm.mapped_column(_sa.Text)
    is_active: _orm.Mapped[bool] = _orm.mapped_column(server_default=_sa.true())
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())
    updated_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(
        server_default=_sa.func.current_timestamp(), onupdate=_sa.func.current_timestamp()
    )


class CategoryBin(_database.Base):
    __tablename__ = "category_bins"
    __table_args__ = (_sa.UniqueConstraint("category_id", "bin_id", name="unique_category_bin"),)

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    category_id: _orm.Mapped[int] = _orm.mapped_column(
        _sa.ForeignKey("categories.id", ondelete="CASCADE", name="fk_category")
    )
    bin_id: _orm.Mapped[int] = _orm.mapped_column(_sa.ForeignKey("bins.id", ondelete="CASCADE", name="fk_bin"))
    is_primary: _orm.Mapped[bool] = _orm.mapped_column(server_default=_sa.true())
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())
    updated_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(
        server_default=_sa.func.current_timestamp(), onupdate=_sa.func.current_timestamp()
    )


class DisposalInstruction(_database.Base):
    __tablename__ = "disposal_instructions"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    category_id: _orm.Mapped[int] = _orm.mapped_column(
        _sa.ForeignKey("categories.id", ondelete="CASCADE", name="fk_instruction_category")
    )
    instructions: _orm.Mapped[str] = _orm.mapped_column(_sa.Text)
    notes: _orm.Mapped[str | None] = _orm.mapped_column(_sa.Text)
    is_active: _orm.Mapped[bool] = _orm.mapped_column(server_default=_sa.true())
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())
    updated_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(
        server_default=_sa.func.current_timestamp(), onupdate=_sa.func.current_timestamp()
    )

class User(_database.Base):
    __tablename__ = "users"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    email: _orm.Mapped[str] = _orm.mapped_column(_sa.String(255), unique=True)
    password_hash: _orm.Mapped[str] = _orm.mapped_column(_sa.String(255))
    role: _orm.Mapped[str] = _orm.mapped_column(_sa.String(20), server_default="user")
    is_active: _orm.Mapped[bool] = _orm.mapped_column(server_default=_sa.true())
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())
    predictions: _orm.Mapped[list["Prediction"]] = _orm.relationship(back_populates="user")


class Prediction(_database.Base):
    __tablename__ = "predictions"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    image_ref: _orm.Mapped[str | None] = _orm.mapped_column(_sa.String(255))
    predicted_category_id: _orm.Mapped[int | None] = _orm.mapped_column(
        _sa.ForeignKey("categories.id", name="fk_prediction_category")
    )
    confidence: _orm.Mapped[_decimal.Decimal | None] = _orm.mapped_column(_sa.Numeric(5, 4))
    # Retained for compatibility with existing databases. New predictions use
    # the four-model ensemble and leave this historical field unset.
    selected_model: _orm.Mapped[str | None] = _orm.mapped_column(_sa.String(50))
    chosen_bin_id: _orm.Mapped[int | None] = _orm.mapped_column(_sa.ForeignKey("bins.id", name="fk_prediction_bin"))
    is_correct: _orm.Mapped[bool | None]
    user_id: _orm.Mapped[int | None] = _orm.mapped_column(
        _sa.ForeignKey("users.id", name="fk_prediction_user"), index=True
        )    
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(
        server_default=_sa.func.current_timestamp(), index=True
    )
    user: _orm.Mapped["User | None"] = _orm.relationship(back_populates="predictions")


class BinExamination(_database.Base):
    __tablename__ = "bin_examinations"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    prediction_id: _orm.Mapped[int] = _orm.mapped_column(
        _sa.ForeignKey("predictions.id", ondelete="CASCADE", name="fk_bin_examination_prediction"), index=True
    )
    selected_bin_id: _orm.Mapped[int] = _orm.mapped_column(
        _sa.ForeignKey("bins.id", name="fk_bin_examination_bin")
    )
    is_correct: _orm.Mapped[bool] = _orm.mapped_column()
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())


class BlogPost(_database.Base):
    __tablename__ = "blog_posts"

    id: _orm.Mapped[int] = _orm.mapped_column(primary_key=True)
    slug: _orm.Mapped[str] = _orm.mapped_column(_sa.String(100), unique=True)
    title: _orm.Mapped[str] = _orm.mapped_column(_sa.String(200))
    summary: _orm.Mapped[str] = _orm.mapped_column(_sa.Text)
    body: _orm.Mapped[str] = _orm.mapped_column(_sa.Text)
    status: _orm.Mapped[str] = _orm.mapped_column(_sa.String(20))
    created_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(server_default=_sa.func.current_timestamp())
    updated_at: _orm.Mapped[_datetime.datetime] = _orm.mapped_column(
        server_default=_sa.func.current_timestamp(), onupdate=_sa.func.current_timestamp()
    )
