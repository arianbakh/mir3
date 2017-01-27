import sys

from crawler import crawl
from index import create_index, delete_index, check_index
from cluster import cluster
from search import search


methods = {
    'crawl': crawl,
    'create_index': create_index,
    'delete_index': delete_index,
    'check_index': check_index,
    'cluster': cluster,
    'search': search,
}


if sys.argv[1] in methods:
    methods[sys.argv[1]](*sys.argv[2:])
else:
    print('Invalid method')
