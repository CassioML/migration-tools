# Run this with cassio==0.0.7 installed

from cassio.vector import VectorTable

from db import getCQLSession, getCQLKeyspace
from settings import (
    FAKE_DATA_OLD_TABLE,
    VECTOR_DIMENSION,
    NUM_SAMPLE_VECTORS,
    WRITE_BATCH_SIZE,
)

if __name__ == '__main__':
    session = getCQLSession()
    keyspace = getCQLKeyspace()
    #
    vtable = VectorTable(
        session,
        keyspace,
        FAKE_DATA_OLD_TABLE,
        embedding_dimension=VECTOR_DIMENSION,
        primary_key_type="TEXT",
    )
    #
    inserted = 0
    print(f"Starting insertion.")
    while inserted < NUM_SAMPLE_VECTORS:
        todos = min(WRITE_BATCH_SIZE, NUM_SAMPLE_VECTORS - inserted)
        futures = []
        for b in range(todos):
            futures.append(vtable.put_async(
                document=f"document_{inserted}",
                embedding_vector=[(inserted+1) / NUM_SAMPLE_VECTORS] * VECTOR_DIMENSION,
                document_id=f"doc_{inserted}",
                metadata={
                    "document_id": f"doc_{inserted}",
                },
                ttl_seconds=None,
            ))
            inserted += 1
        for f in futures:
            _ = f.result()
        print(f"  Inserted {inserted} (this batch: {len(futures)})")
    print(f"Finished inserting {inserted} rows.")
