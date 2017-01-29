import os
import sys

from elasticsearch import Elasticsearch


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_PAGES_DIR = os.path.join(BASE_DIR, 'pages')


ES_HOST = 'localhost'
ES_PORT = '9200'
ES = Elasticsearch(hosts=[{'host': ES_HOST, 'port': ES_PORT}])
INDEX_NAME = 'mir3'
DOC_TYPE = 'wiki'


K_MEANS_ACCEPTABLE_DIFF = 1
K_MEANS_RETRY = 5
VERY_HIGH_INERTIA = sys.float_info.max
