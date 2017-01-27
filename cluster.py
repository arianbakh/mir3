from elasticsearch.helpers import scan, bulk
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from settings import ES, INDEX_NAME, DOC_TYPE, K_MEANS_ACCEPTABLE_DIFF, K_MEANS_RETRY, VERY_HIGH_INERTIA


def _get_all_documents():
    documents = {
        'ids': [],
        'texts': [],
        'vectors': [],
        'sources': [],  # for debugging
    }
    for document in scan(ES, query={'query': {'match_all': {}}}, index=INDEX_NAME, doc_type=DOC_TYPE):
        documents['ids'].append(document['_id'])

        documents['sources'].append(document['_source'])

        text = document['_source']['analyzed_title'] + ' ' + \
            document['_source']['analyzed_introduction'] + ' ' + \
            document['_source']['analyzed_content']
        documents['texts'].append(text)

    vectorizer = TfidfVectorizer(analyzer='word', min_df=0)
    documents['vectors'] = vectorizer.fit_transform(documents['texts'])

    return documents


def _get_cluster_update_operations(k_limit):
    k_limit = int(k_limit)

    documents = _get_all_documents()

    k = 1
    last_inertia_average = VERY_HIGH_INERTIA
    while k_limit == -1 or k <= k_limit:
        inertia_sum = 0
        for i in range(K_MEANS_RETRY):
            kmeans = KMeans(n_clusters=k).fit(documents['vectors'])
            inertia_sum += kmeans.inertia_
        inertia_average = inertia_sum / K_MEANS_RETRY
        diff = last_inertia_average - inertia_average

        print('k = %d;' % k, 'inertia = %f;' % inertia_average, 'diff = %s' % (str(diff) if diff < 1000000 else 'huge!'))

        if diff < K_MEANS_ACCEPTABLE_DIFF:
            break
        else:
            last_inertia_average = inertia_average
            k += 1
    k -= 1
    print('selected k = %d;' % k)

    kmeans = KMeans(n_clusters=k).fit(documents['vectors'])
    for index, label_id in enumerate(kmeans.labels_.tolist()):
        yield {
            '_op_type': 'update',
            '_index': INDEX_NAME,
            '_type': DOC_TYPE,
            '_id': documents['ids'][index],
            'doc': {
                'cluster.id': label_id,
            }
        }


def _bulk_action(k_limit):
    bulk(ES, _get_cluster_update_operations(k_limit), stats_only=False, chunk_size=100)


def cluster(k_limit):
    _bulk_action(k_limit)
