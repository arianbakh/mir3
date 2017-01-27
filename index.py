import json
import os
import random
from pprint import pprint
from time import sleep

from elasticsearch.helpers import bulk

from analysis import analyze
from settings import ES, INDEX_NAME, DOC_TYPE, PAGES_DIR


def _initialize_index():
    body = {
        'number_of_shards': 1,
        'number_of_replicas': 0,
    }
    ES.indices.create(index=INDEX_NAME, body=body)


def _get_cluster_health():
    return ES.cluster.health()  # JSON format


def _configure_index():
    settings_body = {
        'analysis': {
            'char_filter': {},
            'tokenizer': {},
            'filter': {},
            'analyzer': {
                'custom_analyzer': {
                    'tokenizer': 'standard',
                },
            },
        },
    }

    mapping_body = {
        'properties': {
            'page_link': {
                'type': 'text',
            },
            'title': {
                'type': 'text',
            },
            'analyzed_title': {
                'type': 'text',
            },
            'introduction': {
                'type': 'text',
            },
            'analyzed_introduction': {
                'type': 'text',
            },
            'content': {
                'type': 'text',
            },
            'analyzed_content': {
                'type': 'text',
            },
            'links': {
                'properties': {
                    'url': {
                        'type': 'text',
                    },
                    'text': {
                        'type': 'text',
                    },
                },
            },
            'cluster': {
                'properties': {
                    'id': {
                        'type': 'integer',
                    },
                    'label': {
                        'type': 'text',
                    },
                },
            },
        },
    }

    while _get_cluster_health()['status'] != 'green':
        sleep(0.5)  # seconds
    ES.indices.close(index=INDEX_NAME)
    ES.indices.put_settings(index=INDEX_NAME, body=settings_body)
    ES.indices.open(index=INDEX_NAME)
    ES.indices.put_mapping(index=INDEX_NAME, doc_type=DOC_TYPE, body=mapping_body)


def _get_insert_actions():
    index_file_paths = [
        os.path.join(PAGES_DIR, file_name)
        for file_name in os.listdir(PAGES_DIR)
        if os.path.isfile(os.path.join(PAGES_DIR, file_name)) and file_name.endswith('.json')
    ]
    for index_file_path in index_file_paths:
        with open(index_file_path, 'r') as index_file:
            document_json = json.loads(index_file.read())
            content = ' '.join(document_json['content'])
            yield {
                '_op_type': 'index',
                '_index': INDEX_NAME,
                '_type': DOC_TYPE,
                '_source': {
                    'page_link': document_json['page_link'],
                    'title': document_json['title'],
                    'analyzed_title': analyze(document_json['title']),
                    'introduction': document_json['introduction'],
                    'analyzed_introduction': analyze(document_json['introduction']),
                    'content': content,
                    'analyzed_content': analyze(content),
                    'links': document_json['links'],
                }
            }


def _bulk_action():
    bulk(ES, _get_insert_actions(), stats_only=False, chunk_size=50)


def create_index():
    _initialize_index()
    _configure_index()
    _bulk_action()


def delete_index():
    ES.indices.delete(index=INDEX_NAME)


def check_index():
    search_body = {
        'query': {
            'match_all': {},
        }
    }
    hits = ES.search(index=INDEX_NAME, body=search_body)['hits']['hits']
    truncated_doc_source = random.choice(hits)['_source']
    for field in ['introduction', 'analyzed_introduction', 'content', 'analyzed_content']:
        truncated_doc_source[field] = ['...']
    truncated_doc_source['links'] = [truncated_doc_source['links'][0], '...']
    pprint(truncated_doc_source)
