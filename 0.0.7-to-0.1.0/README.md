# 0.0.7 to 0.1.0

(also 0.0.6 to 0.1.0)

Note: this applies to using the `VectorTable` cassIO class both in the legacy
and the new version. If using another table abstraction for the target table,
some considerations are in order.

## Considerations

This simplistic tool works under a few assumptions:

- reasonably low amount of rows in the table (a few tens of thousands or so?). The point is that there is a full table scan in a loop at the heart of reading the legacy table.
- low frequency of writes to the table by the application. The strategy here would be: run a first migration, then update the app to point to the new table, then re-run the migration to make sure nothing is lost. This would have a transient time of occasional misses (the ones recovered by the second migration run), which are supposedly rare if writes are rare.
- *important*: the vector store undergoes writes of _new_ rows only, i.e. no updates to existing rows. If this is the case, the migration logic needs to be made more sophisticated (with write timestamps and so on, something like `dsbulk` does).

If the migration fails, there is no incremental recovery. It could be added in several ways,
however for the time being one should re-launch the whole process.

In order to save on data transfer costs, reduce latencies (and possibly mitigate
timeouts), it is recommended that the migration be run from within the same
cloud provider and region as the database.

_Tested from a home internet connection to Astra DB with 10k rows._

## Setup

Set your secrets: `cp template.env .env` and edit accordingly.

Note that there are two "source" table names defined: one is for a hypothetical
"real" source table, another where, if you want, you can generate synthetic
data to test the process.

## (optional) Generate fake data

This just sets up a table as created by 0.0.7 with a bunch of stuff in it.
In a real setting this table is the one that already exists.

To _emulate_ (that is, to test this migration on generated data),
check `settings.py`, source your `../.env` and launch
`create.py`.

## Migrate

Now for the migration you should **switch to cassio==0.1.0**
and let the library handle the target table for you, including creating it.

Note: even for a real migration (no "setup" step above), adjust `settings.py`
to your preferences. Source `. ../.env` and then run `migrate.py`.

The migration will read data from the `OLD_TABLE` as defined in
`settings.py`: it is up to you
to set this table name equal (or not) to the fake-data-table
you may have generated earlier.

The `migrate.py` script will read from the legacy table with straight CQL
and use the cassIO (`0.1.0`) abstraction to write to the new table.
