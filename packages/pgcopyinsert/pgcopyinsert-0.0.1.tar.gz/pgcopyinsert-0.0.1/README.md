# pgcopyinsert: simple functions for faster PostgreSQL bulk inserts

## What is it?

**pgcopyinsert** is a Python package with simple functions for faster PostgreSQL bulk inserts by copying to temp table then inserting from temp table

## Main Features
Here are just a few of the things that pgcopyinsert does:

  - Copy CSV directly to database table
  - Create temp table based of database table columns (names and types, no constraints)
  - Copy CSV to temp table then insert records from temp table to target table
  - "ON CONFLICT DO NOTHING" and "ON CONFLICT DO UPDATE" insert options
  - 3X faster inserts for Pandas DataFrames
  - Polars DataFrame upserts


## Where to get it
The source code is currently hosted on GitHub at:
https://github.com/eddiethedean/pgcopyinsert

```sh
# PyPI
pip install pgcopyinsert
```

## Dependencies
- [psycopg2](https://www.psycopg.org/docs/)
- [sqlalchemy](https://pypi.org/project/SQLAlchemy/1.3.18/)
- [polars](https://pola.rs)
- [pandas](https://pandas.pydata.org/)

# Example code
```sh
import sqlalchemy as sa
import pgcopyinsert as ci

engine = sa.create_engine('postgresql+pyscopg2://scott:tiger@hostname/dbname')

# Copy CSV directly to database table
with open('data.csv', 'r') as csv_f:
    ci.copy_csv(csv_f, 'table_name', 'table_name_temp', engine, schema='test')

# Create temp table based of database table columns (names and types, no constraints)
meta = sa.MetaData()
meta.reflect(engine)
table = sa.Table('table_name', meta)
temp_table = ci.create_temp_table_from_table(table, 'table_name_temp', meta)

# Copy CSV to temp table then insert records from temp table to target table
with open('data.csv', 'r') as csv_f:
    ci.copyinsert_csv(csv_file, 'table_name_temp', 'table_name_temp', engine)

# "ON CONFLICT DO NOTHING" and "ON CONFLICT DO UPDATE" insert options
on_conflict_do_nothing = ci.insert_from_table_stmt_ocdn
on_conflict_do_update = ci.insert_from_table_stmt_ocdu

with open('data.csv', 'r') as csv_f:
    ci.copyinsert_csv(csv_file, 'table_name_temp', 'table_name_temp', engine, insert_function=on_conflict_do_nothing)

with open('data.csv', 'r') as csv_f:
    ci.copyinsert_csv(csv_file, 'table_name_temp', 'table_name_temp', engine, insert_function=on_conflict_do_update)

# 3X faster inserts for Pandas DataFrames
import pandas as pd

df = pd.DataFrame({'x': range(1_000_000), 'y': range(1_000_000)})
ci.copyinsert_dataframe(df, 'xy_table', 'xy_table_temp', engine)

# Polars DataFrame upserts
import polars as pl

df = pl.DataFrame({'x': range(1_000_000), 'y': range(1_000_000)})
ci.copyinsert_polars(df, 'xy_table', 'xy_table_temp', engine, insert_function=on_conflict_do_update)
```