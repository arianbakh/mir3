import json
import os
import sys
from copy import deepcopy
from urllib.parse import urljoin, urlparse

import urllib3
from bs4 import BeautifulSoup

from settings import DEFAULT_PAGES_DIR


urllib3.disable_warnings()  # InsecureRequestWarning


class Page():
    @staticmethod
    def _get_page_source(url):
        http = urllib3.PoolManager()
        response = http.request('GET', url)
        return response.data

    @staticmethod
    def _is_absolute(url):
        return bool(urlparse(url).netloc)

    @staticmethod
    def _remove_parameters(url):
        parsed = urlparse(url)
        return parsed.scheme + '://' + parsed.netloc + parsed.path

    def _clean_url(self, url):
        """
        convert relative links to absolute + remove parameters +
        remove links to somewhere in the same page +
        remove urls that don't point to a wiki page in persian wikipedia
        """
        if not url or url.startswith('#') or ':' in url:
            return None

        if not Page._is_absolute(url):
            url = urljoin(self.link, url)

        if 'fa.wikipedia.org/wiki' not in url:
            return None

        url = Page._remove_parameters(url)

        return url

    def __init__(self, link):
        self.link = link

        self.data = {'page_link': link}
        page_source = Page._get_page_source(link)
        page_soup = BeautifulSoup(page_source, 'html.parser')

        # remove script tags
        [s.extract() for s in page_soup('script')]

        title_text = page_soup.find(id='firstHeading').get_text().strip()
        self.data['title'] = title_text

        content_soup = page_soup.find(id='mw-content-text')
        worthy_content_soups = content_soup.find_all(['p', 'blockquote'],
                                                     recursive=False)
        introduction_set = False
        self.data['content'] = []
        self.data['introduction'] = ''
        for worthy_content_soup in worthy_content_soups:
            worthy_content_text = worthy_content_soup.get_text().strip()
            if worthy_content_text:  # don't append empty strings
                if worthy_content_soup.name == 'p' and not introduction_set:
                    self.data['introduction'] = worthy_content_text
                    introduction_set = True
                else:
                    self.data['content'].append(worthy_content_text)

        self.data['links'] = []
        for link_in_page in page_soup.find_all('a'):
            url = self._clean_url(link_in_page.get('href'))
            text = link_in_page.get_text().strip()
            if url:  # don't append empty links
                self.data['links'].append({
                    'url': url,
                    'text': text,
                })
        if 'introduction' not in self.data:
            print("OH OH!", link)

    def crawlable_urls(self):
        return [x['url'] for x in self.data['links']]

    def json(self):
        return self.data


def _update_progress(count, max):
    sys.stdout.write('\r[%d/%d]' % (count, max))
    sys.stdout.flush()


def crawl(out_degree, max_pages, input_pages, pages_dir):
    queue = list(deepcopy(input_pages))
    index = 0
    crawled_page_objects = list()
    crawled_page_urls = set()
    _update_progress(0, max_pages)
    while len(crawled_page_urls) < max_pages and index < len(queue):
        page_url = queue[index]
        if page_url not in crawled_page_urls:
            page = Page(page_url)
            crawled_page_objects.append(page)
            queue += page.crawlable_urls()[:out_degree]
            crawled_page_urls.add(page_url)
            _update_progress(len(crawled_page_urls), max_pages)
        index += 1
    print()  # newline after progress bar

    for i, page in enumerate(crawled_page_objects):
        with open(os.path.join(pages_dir, '%d.json' % i), 'w') as output_file:
            output_file.write('%s' % json.dumps(page.json()))
