from urllib.parse import parse_qs as original_parse_qs
from urllib.parse import _coerce_args

from purl import URL as PURL_URL
from purl.url import (
    dict_to_unicode, six, to_unicode, to_utf8, unicode_urlencode, unquote
)


def parse_qsl_with_semicolon_and_not_unquote(
        qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace'):
    """
    This function was copied and modified from https://hg.python.org/cpython/file/3.4/Lib/urllib/parse.py
    to test quickly, will probably need refactor in the future.

    Parse a query given as a string argument.

    Arguments:

    qs: percent-encoded query string to be parsed

    keep_blank_values: flag indicating whether blank values in
        percent-encoded queries should be treated as blank strings.  A
        true value indicates that blanks should be retained as blank
        strings.  The default false value indicates that blank values
        are to be ignored and treated as if they were  not included.

    strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.

    encoding and errors: specify how to decode percent-encoded sequences
        into Unicode characters, as accepted by the bytes.decode() method.

    Returns a list, as G-d intended.
    """
    qs, _coerce_result = _coerce_args(qs)
    pairs = [s1 for s1 in qs.split('&')]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise ValueError("bad query field: %r" % (name_value,))
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = nv[0].replace('+', ' ')
            name = unquote(name, encoding=encoding, errors=errors)
            name = _coerce_result(name)
            value = nv[1]
            r.append((name, value))
    return r


def parse_qs_with_semicolon_and_not_unquote(
        qs, keep_blank_values=False, strict_parsing=False, encoding='utf-8', errors='replace'):
    """
    This function was copied and modified from https://hg.python.org/cpython/file/3.4/Lib/urllib/parse.py
    to test quickly, will probably need refactor in the future.

    Parse a query given as a string argument.

    Arguments:

    qs: percent-encoded query string to be parsed

    keep_blank_values: flag indicating whether blank values in
        percent-encoded queries should be treated as blank strings.
        A true value indicates that blanks should be retained as
        blank strings.  The default false value indicates that
        blank values are to be ignored and treated as if they were
        not included.

    strict_parsing: flag indicating what to do with parsing errors.
        If false (the default), errors are silently ignored.
        If true, errors raise a ValueError exception.

    encoding and errors: specify how to decode percent-encoded sequences
        into Unicode characters, as accepted by the bytes.decode() method.
    """
    parsed_result = {}
    pairs = parse_qsl_with_semicolon_and_not_unquote(
        qs, keep_blank_values, strict_parsing, encoding=encoding, errors=errors)
    for name, value in pairs:
        if name in parsed_result:
            parsed_result[name].append(value)
        else:
            parsed_result[name] = [value]
    return parsed_result


class URL(PURL_URL):

    def query_param_with_semicolon_and_not_unquote(self, key, value=None, default=None, as_list=False):
        return self._query_param(
            key, value=value, default=default, as_list=as_list,
            func=self.query_params_with_semicolon_and_not_unquote)

    def query_param_in_path(self, key, value=None, default=None, as_list=False, func=None):
        return self._query_param(
            key, value=value, default=default, as_list=as_list,
            func=self.query_params_in_path)

    def _query_param(self, key, value=None, default=None, as_list=False, func=None):
        """
        This function was copied and modified from https://github.com/codeinthehole/purl/blob/master/purl/url.py
        to test quickly, will probably need refactor in the future.

        Return or set a query parameter for the given key
        The value can be a list.
        :param string key: key to look for
        :param string default: value to return if ``key`` isn't found
        :param boolean as_list: whether to return the values as a list
        :param string value: the new query parameter to use
        """
        if func is None:
            func = self.query_params

        parse_result = func()

        if value is not None:
            # Need to ensure all strings are unicode
            if isinstance(value, (list, tuple)):
                value = list(map(to_unicode, value))
            else:
                value = to_unicode(value)
            parse_result[to_unicode(key)] = value
            return URL._mutate(
                self, query=unicode_urlencode(parse_result, doseq=True))

        try:
            result = parse_result[key]
        except KeyError:
            return default
        if as_list:
            return result
        return result[0] if len(result) == 1 else result

    def query_params_with_semicolon_and_not_unquote(self, value=None):

        query = '' if self._tuple.query is None else self._tuple.query

        return self._query_params(value=value, qs_func=parse_qs_with_semicolon_and_not_unquote, query=query)

    def query_params_in_path(self, value=None):

        path = '' if self._tuple.path is None else self._tuple.path

        return self._query_params(value=value, qs_func=original_parse_qs, query=path)

    def _query_params(self, value=None, qs_func=None, query=None):
        """
        This function was copied and modified from https://github.com/codeinthehole/purl/blob/master/purl/url.py
        to test quickly, will probably need refactor in the future.

        Return or set a dictionary of query params
        :param dict value: new dictionary of values
        """
        if value is not None:
            return URL._mutate(self, query=unicode_urlencode(value, doseq=True))

        if qs_func is None:
            qs_func = original_parse_qs

        if query is None:
            query = '' if self._tuple.query is None else self._tuple.query

        # In Python 2.6, urlparse needs a bytestring so we encode and then
        # decode the result.
        if not six.PY3:
            result = qs_func(to_utf8(query), True)
            return dict_to_unicode(result)

        return qs_func(query, True)
