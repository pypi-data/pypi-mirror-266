import factory
import faker

from regex_match.objects.parsers import UrlParser

faker = faker.Factory.create()


class UrlParserMethodFactory(factory.Factory):
    class Meta:
        model = UrlParser

    url = faker.url()


class ModelRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.ModelRule'


class ModelExceptionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.ModelException'

    name = faker.name()
    template = '{scheme}://{host}{path}?v={query}'
    model_field = 'url'
    model_field_type = 'url'


class ExceptionParserFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.ExceptionParser'
    model_exception = factory.SubFactory('regex_match.ModelException')


class MatchingRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.MatchingRule'

    model_rule = factory.SubFactory(ModelRuleFactory)


class ParserMethodFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.ParserMethod'
        django_get_or_create = ('name',)


class RegexRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'regex_match.RegexRule'

    matching_rule = factory.SubFactory(MatchingRuleFactory)
    parser_method = factory.SubFactory(ParserMethodFactory)
