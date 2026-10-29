import fastapi as _fastapi
import sqlalchemy as _sa

import app.dependencies as _dependencies
import app.models as _models
import app.schemas as _schemas

router = _fastapi.APIRouter(
    prefix="/blog",
    tags=["blog"],
)


@router.get(
    "/posts",
    response_model=list[_schemas.BlogPostSummary],
)
def list_posts(db: _dependencies.Session):
    posts = db.scalars(
        _sa.select(_models.BlogPost)
        .where(_models.BlogPost.status == "published")
        .order_by(_models.BlogPost.created_at.desc())
    )
    return [
        _schemas.BlogPostSummary(
            slug=post.slug,
            title=post.title,
            summary=post.summary,
            created_at=post.created_at,
        )
        for post in posts
    ]


@router.get(
    "/posts/{slug}",
    response_model=_schemas.BlogPostRead,
)
def get_post(slug: str, db: _dependencies.Session):
    post = db.scalar(
        _sa.select(_models.BlogPost).where(
            _models.BlogPost.slug == slug,
            _models.BlogPost.status == "published",
        )
    )
    if post is None:
        raise _fastapi.HTTPException(
            status_code=_fastapi.status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return _schemas.BlogPostRead(
        slug=post.slug,
        title=post.title,
        summary=post.summary,
        body=post.body,
        created_at=post.created_at,
    )
