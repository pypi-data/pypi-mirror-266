# Flask-DbMigrant

Flask extension for working with Alembic.

It can be used as an alternative for Flask-Migrate. It depends only on Flask and Alembic.

## Installation

```bash
$ pip install Flask-DbMigrant
```

## Usage

First create the `dbmigrant` object:

```python
from flask_dbmigrant import DbMigrant
dbmigrant = DbMigrant()
```

Then initialize it using init_app method:

```python
dbmigrant.init_app(app)  # app is your Flask app instance
```
The Flask app config should have `DB_MODULE` and `DATABASE_URL` keys.

`DB_MODULE` is a name of the module from which database models and metadata are to be imported.

`DATABASE_URL` is a connection string that tells what database to connect to.

## Existing commands

- flask db init

  create a migration repository and configure the environment


- flask db migrate

  create a migration script


- flask db upgrade

  execute the script



## License

`Flask-DbMigrant` was created by Rafal Padkowski. It is licensed under the terms
of the MIT license.
