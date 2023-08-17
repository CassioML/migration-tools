# Run this with cassio==0.1.0 installed

import json

from cassio.table.tables import MetadataVectorCassandraTable

from db import getCQLSession, getCQLKeyspace
from settings import (
    OLD_TABLE,
    TARGET_TABLE,
    VECTOR_DIMENSION,
    WRITE_BATCH_SIZE,
)


def flush_writes(vtable, put_payloads, so_far=None):
    print(f"  Inserting {len(put_payloads)} rows (so far: {so_far})")
    futures = [vtable.put_async(**pload) for pload in put_payloads]
    for f in futures:
        _ = f.result()
    return len(put_payloads)


def legacy_row_to_put_payload(legacy_row):
    """Input is a NamedTuple, output is a kwargs-type dict."""
    return {
        "row_id": legacy_row.document_id,
        "metadata": json.loads(legacy_row.metadata_blob),
        "body_blob": legacy_row.document,
        "vector": legacy_row.embedding_vector,
    }


if __name__ == '__main__':
    print("***************************************************************")
    print("*** PLEASE ENSURE YOU ARE USING CASSIO 0.1.0 IN THIS SCRIPT ***")
    print("***************************************************************")
    #
    session = getCQLSession()
    keyspace = getCQLKeyspace()
    #
    target_vtable = MetadataVectorCassandraTable(
        session,
        keyspace,
        TARGET_TABLE,
        vector_dimension=VECTOR_DIMENSION,
        primary_key_type="TEXT",
        metadata_indexing="all",
    )
    #
    source_reader = session.execute(
        f"SELECT * FROM {keyspace}.{OLD_TABLE} ALLOW FILTERING;"
    )
    # batch insertions on iterator-based reads:
    to_insert = []
    inserted = 0
    print(f"Starting migration.")
    for row in source_reader:
        to_insert.append(legacy_row_to_put_payload(row))
        if len(to_insert) >= WRITE_BATCH_SIZE:
            inserted += flush_writes(target_vtable, to_insert, so_far=inserted)
            to_insert = []
    if len(to_insert) > 0:
        inserted += flush_writes(target_vtable, to_insert, so_far=inserted)
        to_insert = []
    print(f"Finished migrating {inserted} rows.")
