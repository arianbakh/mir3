from analysis import analyze
from settings import ES, INDEX_NAME


def search(query, title_weight, introduction_weight, content_weight,
           cluster_id):
    title_weight = float(title_weight)
    introduction_weight = float(introduction_weight)
    content_weight = float(content_weight)
    cluster_id = int(cluster_id)

    search_body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'multi_match': {
                            'query': analyze(query),
                            'fields': [
                                'analyzed_title^%f' % title_weight,
                                'analyzed_introduction^%f' %
                                introduction_weight,
                                'analyzed_content^%f' % content_weight,
                            ],
                        },
                    },
                ],
            },
        },
    }
    if cluster_id >= 0:
        search_body['query']['bool']['must'].append({
            'term': {
                'cluster.id': cluster_id,
            },
        })
    hits = ES.search(index=INDEX_NAME, body=search_body)['hits']['hits']
    for hit in hits:
        print('id:', hit['_id'])
        print('link:', hit['_source']['page_link'])
        print('title:', hit['_source']['title'])
        print('cluster_id:', hit['_source']['cluster.id'])
        print()
