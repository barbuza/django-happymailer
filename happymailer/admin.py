import json

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseBadRequest

from . import fake
from .models import TemplateModel
from .utils import layout_classes, template_classes, get_template, get_layout


class TemplateAdminForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.Textarea(attrs={'class': 'vLargeTextField'}))
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
    body = forms.CharField(required=False)
    subject = forms.CharField(required=False)
    variables = forms.CharField()

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
        extras = [
            url(r'^preview/$', self.preview, name='%s_%s_preview' % info),
            url(r'^send_test/$', self.send_test, name='%s_%s_send_test' % info)
        ]
        return extras + super(TemplateAdmin, self).get_urls()

    def preview(self, request):
        form = FakedataForm(request.POST)
        if not form.is_valid():
            print(form.errors)
            return HttpResponseBadRequest()
        variables = json.loads(form.cleaned_data['variables'])
        template_cls = get_template(form.cleaned_data['template'])
        layout_cls = get_layout(form.cleaned_data['layout'])
        kwargs = fake.generate(template_cls.kwargs)
        tmpl = template_cls('spam', _force_layout_cls=layout_cls, _force_variables=variables, **kwargs)
        tmpl.body = form.cleaned_data['body']

        return JsonResponse({
            'html': tmpl.compile()
        })

    def send_test(self, request):
        form = FakedataForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        template_cls = get_template(form.cleaned_data['template'])
        layout_cls = get_layout(form.cleaned_data['layout'])
        kwargs = fake.generate(template_cls.kwargs)
        recipient = '{} <{}>'.format(request.user.get_full_name(), request.user.email)
        tmpl = template_cls(recipient, _force_layout_cls=layout_cls, **kwargs)
        tmpl.body = form.cleaned_data['body']
        tmpl.subject = form.cleaned_data['subject']
        tmpl.send()

        return JsonResponse({
            'mail': request.user.email
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

        variables = template.fake_variables()

        extra_context = dict(
            extra_context or {},
            happymailer_config=json.dumps({
                'staticUrl': settings.STATIC_URL + 'happymailer/',
                'template': {
                    'template': model.name,
                    'body': model.body or '',
                    'layout': model.layout or layout_classes[0].name,
                    'enabled': model.enabled,
                    'subject': model.subject or ''
                },
                'previewUrl': reverse('admin:happymailer_templatemodel_preview'),
                'layouts': [{'value': cls.name, 'label': cls.description or cls.name}
                            for cls in layout_classes],
                'variables': [{'name': x.name,
                               'type': repr(x.trafaret),
                               'value': variables.get(x.name, fake.generate(x.trafaret))}
                              for x in template.variables.keys]
            }).replace('<', '\\u003C'),
        )
        return super(TemplateAdmin, self).changeform_view(request, object_id, form_url, extra_context)
