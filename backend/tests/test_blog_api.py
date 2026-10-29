import datetime as _datetime

import fastapi.testclient as _testclient
import pytest as _pytest
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import sqlalchemy.pool as _pool

import app.database as _database
import app.main as _main
import app.models as _models


@_pytest.fixture
def api():
    engine = _sa.create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=_pool.StaticPool,
    )
    _database.Base.metadata.create_all(engine)
    db = _orm.Session(engine)

    db.add_all(
        [
            _models.BlogPost(
                slug="contamination-prevention",
                title="Stopping contamination before it starts",
                summary="Why one greasy pizza box can spoil a whole batch of recycling.",
                body="Full article body about contamination prevention.",
                status="published",
            ),
            _models.BlogPost(
                slug="draft-post",
                title="Not ready yet",
                summary="Should never be visible.",
                body="Draft body.",
                status="draft",
            ),
        ]
    )
    db.commit()

    def get_db():
        yield db

    _main.app.dependency_overrides[_database.get_db] = get_db
    client = _testclient.TestClient(_main.app)
    yield client, db
    _main.app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def test_list_returns_only_published_summaries(api):
    client, _ = api
    response = client.get("/blog/posts")
    assert response.status_code == 200
    assert response.json() == [
        {
            "slug": "contamination-prevention",
            "title": "Stopping contamination before it starts",
            "summary": "Why one greasy pizza box can spoil a whole batch of recycling.",
            "created_at": response.json()[0]["created_at"],
        }
    ]


def test_list_never_includes_body(api):
    client, _ = api
    assert "body" not in client.get("/blog/posts").json()[0]


def test_detail_returns_the_full_published_post(api):
    client, _ = api
    response = client.get("/blog/posts/contamination-prevention")
    assert response.status_code == 200
    assert response.json()["body"] == "Full article body about contamination prevention."


def test_draft_post_is_not_exposed_by_list(api):
    client, _ = api
    slugs = [post["slug"] for post in client.get("/blog/posts").json()]
    assert "draft-post" not in slugs


def test_draft_post_detail_returns_404(api):
    client, _ = api
    assert client.get("/blog/posts/draft-post").status_code == 404


def test_unknown_slug_returns_404(api):
    client, _ = api
    assert client.get("/blog/posts/does-not-exist").status_code == 404


def test_list_returns_newest_first(api):
    client, db = api
    db.add_all(
        [
            _models.BlogPost(
                slug="older-post",
                title="Older",
                summary="s",
                body="b",
                status="published",
                created_at=_datetime.datetime(2026, 7, 1, 10, 0),
            ),
            _models.BlogPost(
                slug="newer-post",
                title="Newer",
                summary="s",
                body="b",
                status="published",
                created_at=_datetime.datetime(2026, 7, 20, 10, 0),
            ),
        ]
    )
    db.commit()

    slugs = [post["slug"] for post in client.get("/blog/posts").json()]
    assert slugs.index("newer-post") < slugs.index("older-post")


def test_empty_blog_returns_empty_list(api):
    client, db = api
    db.execute(_sa.delete(_models.BlogPost))
    db.commit()
    assert client.get("/blog/posts").json() == []
