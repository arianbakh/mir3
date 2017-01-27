import math

from elasticsearch.helpers import scan, bulk
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from settings import ES, INDEX_NAME, DOC_TYPE, K_MEANS_ACCEPTABLE_DIFF, K_MEANS_RETRY, VERY_HIGH_INERTIA


def _get_documents_and_features():
    documents = {
        'ids': [],
        'texts': [],
        'vectors': [],
    }
    features = set()
    for document in scan(ES, query={'query': {'match_all': {}}}, index=INDEX_NAME, doc_type=DOC_TYPE):
        documents['ids'].append(document['_id'])

        text = document['_source']['analyzed_title'] + ' ' + \
            document['_source']['analyzed_introduction'] + ' ' + \
            document['_source']['analyzed_content']
        documents['texts'].append(text)

        for token in document['_source']['analyzed_title'].split() + document['_source']['analyzed_introduction'].split():
            features.add(token)

    vectorizer = TfidfVectorizer(analyzer='word', min_df=0)
    documents['vectors'] = vectorizer.fit_transform(documents['texts'])

    return documents, list(features)


def _get_k(k_limit, documents):
    k_limit = int(k_limit)

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
    return k


def _get_cluster_update_operations(k, documents):
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


def _get_mutual_information(feature, label_id):
    """
    http://nlp.stanford.edu/IR-book/html/htmledition/mutual-information-1.html
    """
    n11 = ES.count(index=INDEX_NAME, body={
        'query': {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': feature,
                            'fields': ['analyzed_title', 'analyzed_introduction', 'analyzed_content'],
                        },
                    },
                    {
                        'term': {
                            'cluster.id': label_id,
                        },
                    },
                ],
            },
        },
    })['count']
    n10 = ES.count(index=INDEX_NAME, body={
        'query': {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': feature,
                            'fields': ['analyzed_title', 'analyzed_introduction', 'analyzed_content'],
                        },
                    },
                ],
                'must_not': [
                    {
                        'term': {
                            'cluster.id': label_id,
                        },
                    },
                ],
            },
        },
    })['count']
    n01 = ES.count(index=INDEX_NAME, body={
        'query': {
            'bool': {
                'must': [
                    {
                        'term': {
                            'cluster.id': label_id,
                        },
                    },
                ],
                'must_not': [
                    {
                        'multi_match': {
                            'query': feature,
                            'fields': ['analyzed_title', 'analyzed_introduction', 'analyzed_content'],
                        },
                    },
                ],
            },
        },
    })['count']
    n00 = ES.count(index=INDEX_NAME, body={
        'query': {
            'bool': {
                'must_not': [
                    {
                        'multi_match': {
                            'query': feature,
                            'fields': ['analyzed_title', 'analyzed_introduction', 'analyzed_content'],
                        },
                    },
                    {
                        'term': {
                            'cluster.id': label_id,
                        },
                    },
                ],
            },
        },
    })['count']
    n1x = float(n10 + n11) or 1.0
    nx1 = float(n01 + n11) or 1.0
    n0x = float(n00 + n01) or 1.0
    nx0 = float(n00 + n10) or 1.0
    n = float(n00 + n01 + n10 + n11) or 1.0

    result = 0
    try:
        result += (n11 / n) * math.log2((n * n11) / (n1x * nx1))
    except ValueError:
        pass
    try:
        result += (n01 / n) * math.log2((n * n01) / (n0x * nx1))
    except ValueError:
        pass
    try:
        result += (n10 / n) * math.log2((n * n10) / (n1x * nx0))
    except ValueError:
        pass
    try:
        result += (n00 / n) * math.log2((n * n00) / (n0x * nx0))
    except ValueError:
        pass
    return result


def _get_cluster_labels(k, features):
    print('finding cluster labels...')
    cluster_to_labels = {}
    for i in range(k):
        cluster_to_labels[i] = []
        for feature in features:
            cluster_to_labels[i].append([_get_mutual_information(feature, i), feature])
    for cluster_id, possible_cluster_labels in cluster_to_labels.items():
        labels = [item[1] for item in sorted(possible_cluster_labels, key=lambda x: -x[0])[:5]]
        print('cluster_id = %s;' % cluster_id, 'labels = %s;' % str(labels))


def cluster(k_limit):
    documents, features = _get_documents_and_features()
    k = _get_k(k_limit, documents)
    bulk(ES, _get_cluster_update_operations(k, documents), stats_only=False, chunk_size=100)
    _get_cluster_labels(k, features)
