from django.db import models
from django.utils import timezone

__all__ = ('TemplateModel', 'HistoricalTemplate',)


class TemplateModelQueryset(models.QuerySet):
    def active(self):
        return self.filter(enabled=True, has_errors=False)


class TemplateModel(models.Model):
    """
    stores editable template data
    """
    name = models.SlugField(unique=True)
    layout = models.SlugField(null=True)
    subject = models.TextField(null=True)
    body = models.TextField(null=True)
    version = models.IntegerField(default=1)
    enabled = models.BooleanField(default=False)
    has_errors = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
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
    template = models.ForeignKey(TemplateModel, related_name='history', on_delete=models.CASCADE)
    layout = models.SlugField(null=True)
    subject = models.TextField(null=True)
    body = models.TextField()
    version = models.IntegerField()
    archived_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s' % self.version

    class Meta:
        ordering = ('-version',)
