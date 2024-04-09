from django.db import models


class MatchingRule(models.Model):
    model_rule = models.ForeignKey(
        "ModelRule", on_delete=models.CASCADE, related_name="matching_rules"
    )
    description = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "{} match [{}]".format(self.model_rule, self._get_regex_rules())

    def _get_regex_rules(self):
        matches = self.regex_rules.all()
        matches_map = map(self._get_match_rule_name, matches)

        return ", ".join(list(matches_map))

    def _get_match_rule_name(self, match):
        return "{} | {}".format(match.parser_method.name, match.regex)

    def is_valid(self):
        return len(self.regex_rules.all()) > 0
