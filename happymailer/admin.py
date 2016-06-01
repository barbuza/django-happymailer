from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.http import Http404, JsonResponse, HttpResponseBadRequest

from . import fake
from .models import TemplateModel
from .utils import layout_classes, template_classes, get_template, get_layout


class TemplateAdminForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'vLargeTextField'}))
    layout = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(TemplateAdminForm, self).__init__(*args, **kwargs)
        self.fields['layout'].choices = [(cls.name, cls.description or cls.name) for cls in layout_classes]

    class Meta:
        model = TemplateModel
        fields = ('layout', 'subject', 'body', 'enabled',)


class FakedataForm(forms.Form):
    layout = forms.CharField()
    template = forms.CharField()
    body = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(FakedataForm, self).__init__(*args, **kwargs)
        self.fields['layout'].choices = [(cls.name, cls.name) for cls in layout_classes]
        self.fields['template'].choices = [(cls.name, cls.name) for cls in template_classes]


@admin.register(TemplateModel)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'version',)
    readonly_fields = ('name',)
    form = TemplateAdminForm
    fields = ('name', 'enabled', 'layout', 'subject', 'body',)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        extras = [url(r'^preview/$', self.preview, name='%s_%s_preview' % info)]
        return extras + super(TemplateAdmin, self).get_urls()

    def preview(self, request):
        form = FakedataForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        template_cls = get_template(form.cleaned_data['template'])
        layout_cls = get_layout(form.cleaned_data['layout'])
        kwargs = fake.generate(template_cls.kwargs)
        tmpl = template_cls('spam', _force_layout_cls=layout_cls, **kwargs)
        tmpl.body = form.cleaned_data['body']

        return JsonResponse({
            'html': tmpl.compile(),
            'variables': {name: repr(value) for name, value in tmpl.variables.items()}
        })

    def get_actions(self, request):
        return None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            model = TemplateModel.objects.get(pk=object_id)
        except TemplateModel.DoesNotExist:
            raise Http404()

        template = None
        for cls in template_classes:
            if cls.name == model.name:
                template = cls

        if not template:
            raise Http404()

        extra_context = dict(
            extra_context or {},
            variables=[{'name': x.name, 'value': repr(x.trafaret)}
                       for x in template.variables.keys]
        )
        return super(TemplateAdmin, self).changeform_view(request, object_id, form_url, extra_context)
