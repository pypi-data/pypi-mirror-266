from django.db import models

from .parser import Parser


class ExceptionParser(Parser):
    name = models.CharField(max_length=32)
    model_exception = models.ForeignKey(
        "ModelException", on_delete=models.CASCADE, related_name="parsers"
    )
