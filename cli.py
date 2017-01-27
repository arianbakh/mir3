import sys

from crawler import crawl
from index import create_index, delete_index, check_index


methods = {
    'crawl': crawl,
    'create_index': create_index,
    'delete_index': delete_index,
    'check_index': check_index,
}


if sys.argv[1] in methods:
    methods[sys.argv[1]](*sys.argv[2:])
else:
    print('Invalid method')
