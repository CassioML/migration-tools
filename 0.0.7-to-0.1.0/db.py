import os
from cassandra.cluster import (
    Cluster,
)
from cassandra.auth import PlainTextAuthProvider

ASTRA_DB_SECURE_BUNDLE_PATH = os.environ["ASTRA_DB_SECURE_BUNDLE_PATH"]
ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE"]

LOCAL_KEYSPACE = os.environ.get("LOCAL_KEYSPACE", "UNDEFINED_KEYSPACE")

def getCQLSession(mode='astra_db'):
    if mode == 'astra_db':
        cluster = Cluster(
            cloud={
                "secure_connect_bundle": ASTRA_DB_SECURE_BUNDLE_PATH,
            },
            auth_provider=PlainTextAuthProvider(
                "token",
                ASTRA_DB_APPLICATION_TOKEN,
            ),
        )
        astraSession = cluster.connect()
        return astraSession
    elif mode == 'local':
        cluster = Cluster()
        localSession = cluster.connect()
        return localSession
    else:
        raise ValueError('Unknown CQL Session mode')

def getCQLKeyspace(mode='astra_db'):
    if mode == 'astra_db':
        return ASTRA_DB_KEYSPACE
    elif mode == 'local':
        return LOCAL_KEYSPACE
    else:
        raise ValueError('Unknown CQL Session mode')
