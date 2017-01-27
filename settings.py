import os

from elasticsearch import Elasticsearch


OUT_DEGREE = 10
MAX_PAGES = 10  # TODO 1000
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, 'pages')


ES_HOST = 'localhost'
ES_PORT = '9200'
ES = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}])
INDEX_NAME = 'mir3'
DOC_TYPE = 'wiki'
