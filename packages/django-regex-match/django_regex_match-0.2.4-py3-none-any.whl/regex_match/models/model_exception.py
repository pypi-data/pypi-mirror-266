from django.db import models

from .model_rule import ModelRule


class ModelException(ModelRule):
    name = models.CharField(max_length=32)
    template = models.TextField(null=False)

    def format_template(self, obj):
        parsers_dic = self._parsers_to_dic(obj)

        return self.template.format(**parsers_dic)

    def _parsers_to_dic(self, obj):
        parsers = self.parsers.all()

        return dict([self._compile_parser(parser, obj) for parser in parsers])

    def _compile_parser(self, parser, obj):
        return parser.name, parser.parse_obj(obj)
