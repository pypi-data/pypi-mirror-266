import re
from urllib.parse import urlparse

from .url import URL


class UrlParser(object):

    def __init__(self, url):
        self.url = self._get_valid_url(url)

    def host(self):
        return self.url.host()

    def domain(self):
        return self.url.domain()

    def path(self):
        return self.url.path()

    def fragment(self):
        return self.url.fragment()

    def fragment_split_get_first(self, params):
        return self.url.fragment().split(params, 1)[0]

    def scheme(self):
        return self.url.scheme()

    def query(self):
        return self.url.query()

    def query_param(self, params):
        return self.url.query_param(params)

    @staticmethod
    def _get_valid_url(url):
        converted_url = u'{}'.format(url)

        if not urlparse(converted_url).scheme:
            converted_url = 'http://{}'.format(converted_url)

        return URL(converted_url)

    def query_param_with_semicolon_and_not_unquote(self, params):
        return self.url.query_param_with_semicolon_and_not_unquote(params)

    def query_param_in_path(self, params):
        return self.url.query_param_in_path(params)

    def path_re_search_group(self, params):
        url_part = self.url.path()
        return self._re_search_group(params, url_part)

    def host_re_search_group(self, params):
        url_part = self.url.host()
        return self._re_search_group(params, url_part)

    def domain_re_search_group(self, params):
        url_part = self.url.domain()
        return self._re_search_group(params, url_part)

    def fragment_re_search_group(self, params):
        url_part = self.url.fragment()
        return self._re_search_group(params, url_part)

    def query_re_search_group(self, params):
        url_part = self.url.query()
        return self._re_search_group(params, url_part)

    def _re_search_group(self, params, url_part):
        group = int(params[:1])
        regex = params[2:]
        return re.compile(regex).search(url_part).group(group)
