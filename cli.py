import sys

from crawler import crawl


methods = {
    'crawl': crawl,
}


if sys.argv[1] in methods:
    methods[sys.argv[1]](*sys.argv[2:])
else:
    print('Invalid method')
