"""
Database rebuild/reset script for development.

Explicit utility to rebuild the development database schema and seed data.
NEVER runs automatically on application startup.

Usage:
    python -m app.utils.rebuild_db [--force]
"""
import sys
import argparse
from sqlalchemy import text
from alembic.config import Config
from alembic import command

from app.core.config import settings
from app.database.session import engine, Base
from app.utils.seed import seed


def rebuild(force: bool = False):
    if not force:
        confirm = input(
            f"WARNING: This will drop and rebuild all tables in '{settings.DATABASE_URL.split('/')[-1]}'.\n"
            "Are you sure you want to proceed? [y/N]: "
        )
        if confirm.strip().lower() not in ("y", "yes"):
            print("Operation aborted by user.")
            sys.exit(0)

    print("Step 1: Dropping all database tables...")
    # Drop using raw CASCADE in PostgreSQL to handle foreign key cycles cleanly
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    print("  Schema reset completed.")

    print("Step 2: Running Alembic migrations to head...")
    import os
    alembic_ini_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "alembic.ini",
    )
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, "head")
    print("  Alembic upgrade head completed.")

    print("Step 3: Seeding development data...")
    seed()
    print("Database rebuild and seeding successfully completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild and reseed the development database.")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    rebuild(force=args.force)
