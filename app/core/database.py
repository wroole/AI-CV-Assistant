from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import DATABASE_URL


# ``pool_pre_ping`` issues a lightweight ``SELECT 1`` before reusing a
# connection so that idle connections dropped by Postgres don't cause errors.
# ``pool_recycle`` retires connections after 30 minutes.
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # SQLite needs this for multi-threaded FastAPI.
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models (app.models.*)."""
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped Session.

    Usage in a router::

        @router.get("/me")
        def read_me(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables that are defined on :class:`Base`.

    Useful for quick local development. In production prefer Alembic
    migrations (see ``alembic/``) so schema changes are versioned.
    """
    # Ensure models are imported so their tables are registered on Base.
    from app import models  # noqa: F401  (import side-effect)

    Base.metadata.create_all(bind=engine)
