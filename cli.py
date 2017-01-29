#!/usr/bin/env python
import sys

from cluster import cluster
from crawler import crawl
from index import create_index, delete_index, check_index
from search import search


__methods = {
    'crawl': crawl,
    'create_index': create_index,
    'delete_index': delete_index,
    'check_index': check_index,
    'cluster': cluster,
    'search': search,
}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s COMMAND" % sys.argv[0])
    elif sys.argv[1] in __methods:
        __methods[sys.argv[1]](*sys.argv[2:])
    else:
        print("Invalid method: %s" % sys.argv[1])
