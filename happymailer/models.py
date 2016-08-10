from django.db import models
from django.conf import settings

__all__ = ('TemplateModel', 'HistoricalTemplate',)


class TemplateModelQueryset(models.QuerySet):
    pass


class TemplateModel(models.Model):
    """
    stores editable template data
    """
    name = models.SlugField(unique=True)
    layout = models.SlugField(null=True)
    subject = models.TextField(null=True)
    body = models.TextField(null=True)
    version = models.IntegerField(default=0)
    enabled = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TemplateModelQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Template'
        ordering = ('name',)


class HistoricalTemplate(models.Model):
    """
    stores previous versions of TemplateModel
    """
    template = models.ForeignKey(TemplateModel, related_name='history')
    layout = models.SlugField(null=True)
    subject = models.TextField(null=True)
    body = models.TextField()
    version = models.IntegerField()
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-version',)
