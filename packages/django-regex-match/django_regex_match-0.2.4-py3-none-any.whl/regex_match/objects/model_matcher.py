from django.core.cache import cache
from django.db.models import Q
from funcy import first
from toolz import curry
from toolz.curried import filter, pipe

from regex_match.models.model_rule import ModelRule


class ModelMatcher(object):

    def __init__(self, model, model_field, obj):
        self.obj = obj
        self.model = model
        self.model_field = model_field

    def get(self):
        """
        1) Returns the first object that have a matching matching_rule
        2) A matching_rule is matching if all regex rules are matching
        """

        all_regex_match = self._build_match(
            predicate=self._regex_match,
            fn=all
        )

        regex_predicate = self._match_rule(
            parser_method='regex_rules',
            match=all_regex_match
        )

        any_classification_match = self._build_match(
            predicate=regex_predicate,
            fn=any
        )

        classification_predicate = self._match_rule(
            parser_method='matching_rules',
            match=any_classification_match
        )

        if not isinstance(self.model, str):
            cache_key = hash(self.model) + hash(self.model_field)
            model_rules = cache.get(cache_key)

            if model_rules is None:
                model_rules = self._get_model_rules()
                cache.set(cache_key, model_rules, 30)
        else:
            model_rules = self._get_model_rules()

        return pipe(model_rules, filter(classification_predicate), first)

    @staticmethod
    @curry
    def _match_rule(model_rule, match, parser_method):
        cache_key = hash(model_rule) + hash(match) + hash(parser_method)
        sequence = cache.get(cache_key)

        if sequence is None:
            sequence = list(getattr(model_rule, parser_method).select_related())
            cache.set(cache_key, sequence, 30)

        return match(
            sequence=sequence
        )

    @staticmethod
    @curry
    def _build_match(fn, predicate, sequence):
        """
        Generate match using a fn, a predicate and a sequence of rules
        Returns True, False or an Object depending of the fn
        """
        return fn(
            predicate(item)
            for item in sequence
        )

    def _regex_match(self, rule):
        return rule.is_matching(self.obj)

    def _get_model_rules(self):
        if (type(self.model) == str):
            model = self.model.lower()
        else:
            model = self.model.__name__.lower()

        return list(ModelRule.objects.filter(
            Q(polymorphic_ctype__model=model) &
            Q(model_field=self.model_field)
        ).select_related().prefetch_related())
