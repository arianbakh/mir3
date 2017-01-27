# Requirements

## apt Requirements

1. python 3.4.0

## pip Requirements

1. bs4==0.0.1
2. urllib3==1.19.1
3. elasticsearch==5.0.1
4. scikit-learn==0.18.1

## Elasticsearch

1. an Elasticsearch instance (v5.0.1) must be up and listening on localhost:9200 (preferably docker)

# usage

1. python3 cli.py crawl https://fa.wikipedia.org/wiki/%D8%B3%D8%B9%D8%AF%DB%8C https://fa.wikipedia.org/wiki/%DA%AF%D9%84%D8%B3%D8%AA%D8%A7%D9%86_%D8%B3%D8%B9%D8%AF%DB%8C
2. python3 cli.py create_index
3. python3 cli.py delete_index
4. python3 cli.py check_index

# TODO

1. check the cli is exactly as described
