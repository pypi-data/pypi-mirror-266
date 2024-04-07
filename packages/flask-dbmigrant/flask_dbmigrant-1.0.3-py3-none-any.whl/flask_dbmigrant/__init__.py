import fileinput
import pathlib

import click
from alembic import command as alembic_command
from alembic.config import Config


class DbMigrant:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        DB_MODULE = app.config["DB_MODULE"]
        CONFIG_MODULE = app.config["CONFIG_MODULE"]

        @app.cli.command("db")
        @click.argument("command")
        def db_command(command):
            """Possible commands:

            \b
            init - initialize migrations
            migrate - create a new migration script
            upgrade - upgrade database

            """

            alembic_cfg = Config("alembic.ini")

            match command:
                case "init":
                    alembic_command.init(alembic_cfg, "migrations")

                    backup_file_path = (
                        pathlib.Path("migrations").absolute() / "env.py.bak"
                    )
                    print(f"  Creating backup file '{backup_file_path}' ...", end="  ")

                    with fileinput.FileInput(
                        "migrations/env.py", inplace=True, backup=".bak"
                    ) as f:
                        line = f.readline()
                        print(f"from {CONFIG_MODULE} import DATABASE_URL", end="\n")
                        print(f"import {DB_MODULE}", end="\n")
                        print(line, end="")

                        for line in f:
                            if "target_metadata = None" in line:
                                print(
                                    line.rstrip().replace(
                                        "None", f"{DB_MODULE}.metadata"
                                    )
                                )
                                print(
                                    'config.set_main_option("sqlalchemy.url", DATABASE_URL)'
                                )
                            elif (
                                "connection=connection, target_metadata=target_metadata"
                                in line
                            ):
                                print(line.rstrip() + ", render_as_batch=True")
                            else:
                                print(line, end="")

                    print("done")

                case "migrate":
                    alembic_command.revision(alembic_cfg, autogenerate=True)

                case "upgrade":
                    alembic_command.upgrade(alembic_cfg, "head")
