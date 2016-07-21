from django.http import HttpResponse
from django.conf import settings
from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.formats import base_formats

from .models import TemplateModel


__all__ = ['TemplateImportExportMixin']


class TemplateResource(resources.ModelResource):
    class Meta:
        model = TemplateModel


class TemplateImportExportMixin(ImportExportMixin):
    formats = [base_formats.JSON]

    def export_action(self, request, *args, **kwargs):
        file_format = base_formats.JSON()
        queryset = self.get_export_queryset(request)
        export_data = self.get_export_data(file_format, queryset)
        content_type = file_format.get_content_type()
        response = HttpResponse(export_data, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % (
            self.get_export_filename(file_format),
        )
        return response


class EmptyMixin:
    pass


if 'import_export' not in settings.INSTALLED_APPS:
    TemplateImportExportMixin = EmptyMixin