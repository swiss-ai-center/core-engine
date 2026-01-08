import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Import SQLModel
from sqlmodel import SQLModel  # noqa: E402 F401 F403

# Import all models so they're registered with SQLModel.metadata
from common.models import *  # noqa: E402 F401 F403
from services.models import *  # noqa: E402 F401 F403
from connection_manager.models import *  # noqa: E402 F401 F403
from execution_units.models import *  # noqa: E402 F401 F403
from pipeline_executions.models import *  # noqa: E402 F401 F403
from pipeline_steps.models import *  # noqa: E402 F401 F403
from pipelines.models import *  # noqa: E402 F401 F403
from stats.models import *  # noqa: E402 F401 F403
from storage.models import *  # noqa: E402 F401 F403
from tasks.models import *  # noqa: E402 F401 F403

load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
data_base_url = os.getenv("DATABASE_URL")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# Set target_metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    if data_base_url:
        config.set_main_option("sqlalchemy.url", data_base_url)
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    db_config = config.get_section(config.config_ini_section)
    if data_base_url:
        db_config["sqlalchemy.url"] = data_base_url

    connectable = engine_from_config(
        db_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
