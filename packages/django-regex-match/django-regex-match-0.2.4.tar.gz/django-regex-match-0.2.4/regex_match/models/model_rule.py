from django.db import models
from polymorphic.models import PolymorphicModel


class ModelRule(PolymorphicModel):
    model_field = models.CharField(max_length=16)
    model_field_type = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-priority',)

    def is_valid(self):
        return any(
            self.has_regex_rule(item)
            for item in self.matching_rules.all()
        )

    @staticmethod
    def has_regex_rule(matching_rule):
        return matching_rule.is_valid()
