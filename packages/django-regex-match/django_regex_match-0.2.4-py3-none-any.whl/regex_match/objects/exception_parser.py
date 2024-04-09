from regex_match.objects.model_matcher import ModelMatcher
from regex_match.objects.parsers import UrlParser


class ExceptionParser(object):

    def __init__(self, model, model_field, url):
        self.url = url
        self.obj = UrlParser(url)
        self.match = ModelMatcher(
            model=model,
            model_field=model_field,
            obj=self.obj
        ).get()

    def is_matched(self):
        return self.match is not None

    def format_template(self):
        if self.match:
            return self.match.format_template(self.obj)
        else:
            return self.url
