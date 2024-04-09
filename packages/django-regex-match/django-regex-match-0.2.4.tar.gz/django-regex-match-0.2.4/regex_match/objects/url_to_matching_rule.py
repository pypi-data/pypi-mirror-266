from funcy import keep

from regex_match.models import MatchingRule, ParserMethod, RegexRule
from regex_match.objects.parsers import UrlParser


class UrlToMatchingRule(object):
    default_regex_template_domain = "((^.*[.])|^){}$"
    default_regex_template_path = "^{}(/.*|)$"
    default_regex_template_query = "(^|.+&){}={}($|&.+)"

    def __init__(
        self,
        model_rule,
        urls,
        priority_func=None,
        description="",
        regex_template_domain=None,
        regex_template_path=None,
        regex_template_query=None,
    ):
        self.regex_template_domain = (
            regex_template_domain or self.default_regex_template_domain
        )
        self.regex_template_path = (
            regex_template_path or self.default_regex_template_path
        )
        self.regex_template_query = (
            regex_template_query or self.default_regex_template_query
        )

        self.model_rule = model_rule
        self.urls = urls
        self.priority_func = priority_func
        self.description = description

    def create(self):
        matching_rule_array = keep(self._create_matching_rule, self.urls)
        return list(matching_rule_array)

    def _create_matching_rule(self, url):
        obj = UrlParser(url)

        matching_rule = MatchingRule(
            model_rule=self.model_rule, description=self.description
        )
        matching_rule.save()

        domain_rule = self._create_domain_matching_rule(matching_rule, obj)

        path_rule = self._create_path_matching_rule(
            matching_rule, obj, bool(obj.url.query_params())
        )

        query_rules = self._create_query_matching_rule(matching_rule, obj)

        if self.priority_func is not None:
            self.priority = self.priority_func(domain_rule, path_rule, query_rules)

        return matching_rule

    def _create_domain_matching_rule(self, matching_rule, url):
        if url.domain() != "":

            parser_method = ParserMethod.objects.get(name="domain")
            return RegexRule.objects.create(
                matching_rule=matching_rule,
                parser_method=parser_method,
                regex=self.regex_template_domain.format(
                    url.domain().replace(".", "[.]").replace("+", "[+]")
                ),
            )

    def _create_path_matching_rule(self, matching_rule, url, has_params):
        if url.path() != "":
            regex_template = self.regex_template_path
            parser_method = ParserMethod.objects.get(name="path")
            return RegexRule.objects.create(
                matching_rule=matching_rule,
                parser_method=parser_method,
                regex=regex_template.format(
                    url.path().replace(".", "[.]").replace("+", "[+]")
                ),
            )

    def _create_query_matching_rule(self, matching_rule, url):
        result = list()
        query_params = url.url.query_params()
        for k in query_params:
            parser_method = ParserMethod.objects.get(name="query")
            rule = RegexRule.objects.create(
                matching_rule=matching_rule,
                parser_method=parser_method,
                regex=self.regex_template_query.format(
                    k, url.query_param(k).replace(".", "[.]").replace("+", "[+]")
                ),
            )
            result.append(rule)
        return result
