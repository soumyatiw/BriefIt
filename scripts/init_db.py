import api.models  # noqa: F401 — registers all models on Base.metadata
from api.database import Base, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    tables = list(Base.metadata.tables.keys())
    print(f"Tables created: {', '.join(sorted(tables))}")


if __name__ == "__main__":
    main()
