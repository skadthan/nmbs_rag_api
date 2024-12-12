from app.config import ELASTICSEARCH_URL, ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD,SSL_ASSERT_FINGERPRINT
from elasticsearch import Elasticsearch

def get_es_connection():
    es_client = Elasticsearch(
        ELASTICSEARCH_URL,
        ssl_assert_fingerprint=SSL_ASSERT_FINGERPRINT,
        basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
        )
    return es_client