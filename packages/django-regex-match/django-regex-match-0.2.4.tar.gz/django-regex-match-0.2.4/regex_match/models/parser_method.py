from django.db import models


class ParserMethod(models.Model):
    type = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{}.{}()'.format(self.type, self.name)

    class Meta:
        unique_together = ('name', 'type')
