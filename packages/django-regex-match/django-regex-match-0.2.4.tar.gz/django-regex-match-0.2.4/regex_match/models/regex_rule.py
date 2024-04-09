import re

from django.db import models

from .parser import Parser


class RegexRule(Parser):
    matching_rule = models.ForeignKey(
        "MatchingRule", on_delete=models.CASCADE, related_name="regex_rules"
    )
    regex = models.TextField(null=False)

    def __str__(self):
        return "{} match {}".format(self.method(), self.regex)

    def is_matching(self, obj):
        """
        Test if a regex match a rule's method
        Returns True of False
        """
        matching = False
        regex = re.compile(self.regex)
        string = self.parse_obj(obj)
        if string is not None:
            matching = bool(regex.match(string))
        return matching
