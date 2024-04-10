import logging
import os
from pathlib import Path
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from oslo_config import cfg

import aprsd
from aprsd_irc_extension import conf  # noqaa
from aprsd_irc_extension.db.models import Base
from aprsd.log import log


home = str(Path.home())
DEFAULT_CONFIG_DIR = f"{home}/.config/aprsd/"
DEFAULT_CONFIG_FILE = f"{home}/.config/aprsd/aprsd.conf"


CONF = cfg.CONF
LOG = logging.getLogger("APRSD")

target_metadata = Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# fileConfig(config.config_file_name)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, folder)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = haminfo_db.Station.metadata
# target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
# config_file = context.get_x_argument(as_dictionary=True).get('config_file')
# if not config_file:
print(sys.argv)
config_file = [DEFAULT_CONFIG_FILE]
CONF(
    [], project='aprsd',
    version=aprsd.__version__,
    default_config_files=config_file,
)
log.setup_logging()
# python_logging.captureWarnings(True)
CONF.log_opt_values(LOG, logging.DEBUG)


def get_url():
    url = CONF.aprsd_irc_extension.db_dsn
    assert url, "Couldn't find DB url!!"
    print(f"Using DB URL {url}")
    return url


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    context.config.set_section_option(config.config_ini_section,
                                      "sqlalchemy.url", url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = get_url()
    # connectable = create_engine(url)
    # context.config.set_main_option('sqlalchemy.url', url)
    context.config.set_section_option(config.config_ini_section,
                                      "sqlalchemy.url", url)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
