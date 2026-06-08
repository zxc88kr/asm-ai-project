from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def migrate_sqlite_schema(target_engine=engine):
    """Apply minimal SQLite schema fixes for pre-existing local DB files."""
    if not str(target_engine.url).startswith("sqlite"):
        return

    inspector = inspect(target_engine)
    tables_to_user_column = ("clue_state", "character_state", "chat_message")
    with target_engine.begin() as connection:
        for table_name in tables_to_user_column:
            if table_name not in inspector.get_table_names():
                continue
            column_names = {
                column["name"] for column in inspector.get_columns(table_name)
            }
            if "user_id" not in column_names:
                connection.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        "ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default'"
                    )
                )
            connection.execute(
                text(
                    f"CREATE INDEX IF NOT EXISTS ix_{table_name}_user_id "
                    f"ON {table_name} (user_id)"
                )
            )
