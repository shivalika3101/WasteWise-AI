import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import sqlalchemy.pool as _pool

import app.database as _database
import app.models as _models
import seeds.seed as _seed
import seeds.seed_data as _seed_data


def _session():
    engine = _sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=_pool.StaticPool,
    )
    _database.Base.metadata.create_all(engine)
    return _orm.Session(engine)


def test_seeding_creates_every_configured_post():
    db = _session()
    _seed.seed_blog_posts(db)
    assert db.query(_models.BlogPost).count() == len(_seed_data.BLOG_POSTS)


def test_seeding_twice_does_not_duplicate():
    db = _session()
    _seed.seed_blog_posts(db)
    _seed.seed_blog_posts(db)
    assert db.query(_models.BlogPost).count() == len(_seed_data.BLOG_POSTS)


def test_every_seeded_post_is_published():
    db = _session()
    _seed.seed_blog_posts(db)
    statuses = {post.status for post in db.query(_models.BlogPost)}
    assert statuses == {"published"}


def test_seeded_slugs_are_unique():
    slugs = [post["slug"] for post in _seed_data.BLOG_POSTS]
    assert len(slugs) == len(set(slugs))
