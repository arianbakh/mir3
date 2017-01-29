#!/usr/bin/env python
import argparse

from cluster import cluster
from crawler import crawl
from index import create_index, delete_index
from settings import DEFAULT_PAGES_DIR
from search import search


def handle_default(args):
    args.print_usage()


def handle_crawl(args):
    crawl(args.out_degree, args.num_pages, args.urls, args.json_directory)


def handle_index(args):
    if args.delete_index:
        delete_index()
    else:
        create_index(args.json_directory)


def handle_cluster(args):
    cluster(args.max_k)


def handle_search(args):
    search(args.query, args.title_weight, args.introduction_weight,
           args.content_weight, args.cluster_id)


def add_crawl_parser(subparsers):
    parser = subparsers.add_parser('crawl', description="Crawl wikipedia pages"
                                                        " and save them in"
                                                        " destination folder")
    parser.add_argument('urls', nargs='+', help="starting page url",
                        metavar='url')
    parser.add_argument('-d', '--out-degree', default=10, type=int,
                        help="maximum out-degree of pages")
    parser.add_argument('-p', '--num-pages', default=1000, type=int,
                        help="maximum number of pages to crawl")
    parser.add_argument('-j', '--json-directory', default=DEFAULT_PAGES_DIR,
                        help="Directory to store wikipedia pages data as "
                             "json files")
    parser.set_defaults(handle=handle_crawl)


def add_index_parser(subparsers):
    parser = subparsers.add_parser('index', description="Handle indexing")
    parser.add_argument('-j', '--json-directory', default=DEFAULT_PAGES_DIR,
                        help="Directory to read wikipedia pages data json "
                             "files from")
    parser.add_argument('-d', '--delete-index', action='store_true',
                        help="Delete index")
    parser.set_defaults(handle=handle_index)


def add_cluster_parser(subparsers):
    parser = subparsers.add_parser('cluster', description="Cluster wiki pages")
    parser.add_argument('-k', '--max-k', type=int, default=-1,
                        help="maximum K for K-means algorithm")
    parser.set_defaults(handle=handle_cluster)


def add_search_parser(subparsers):
    parser = subparsers.add_parser('search', description="Search wiki pages")
    parser.add_argument('query')
    parser.add_argument('-t', '--title-weight', type=int, default=1)
    parser.add_argument('-i', '--introduction-weight', type=int, default=1)
    parser.add_argument('-c', '--content-weight', type=int, default=1)
    parser.add_argument('-C', '--cluster-id', type=int, default=-1,
                        help="Cluster id to search within")
    parser.set_defaults(handle=handle_search)


def main():
    parser = argparse.ArgumentParser()
    parser.set_defaults(handle=handle_default, print_usage=parser.print_usage)
    subparsers = parser.add_subparsers(title="commands")
    add_crawl_parser(subparsers)
    add_index_parser(subparsers)
    add_cluster_parser(subparsers)
    add_search_parser(subparsers)
    args = parser.parse_args()
    args.handle(args)

if __name__ == '__main__':
    main() 
