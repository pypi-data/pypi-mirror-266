from django.db import models
from polymorphic.models import PolymorphicModel


class Parser(PolymorphicModel):
    parser_method = models.ForeignKey(
        "ParserMethod", on_delete=models.CASCADE, related_name="parsers"
    )
    parser_method_params = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def method(self):
        # Add a cache system here
        return self.parser_method.name

    def params(self):
        return self.parser_method_params

    def parse_obj(self, obj):
        method = self.method()
        params = self.params()
        parser_method = getattr(obj, method)

        if params:
            return parser_method(params)
        else:
            return parser_method()
