import json

import trafaret
from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.core.urlresolvers import reverse
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.contrib.admin.utils import unquote
from django.core.serializers.json import DjangoJSONEncoder
from django.template.response import TemplateResponse
from django.db import transaction

from . import fake
from .backends.base import CompileError
from .mixins import TemplateImportExportMixin
from .models import TemplateModel, HistoricalTemplate
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
    variables = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(FakedataForm, self).__init__(*args, **kwargs)
        self.fields['layout'].choices = [(cls.name, cls.name) for cls in layout_classes]
        self.fields['template'].choices = [(cls.name, cls.name) for cls in template_classes]


class ImportForm(forms.Form):
    import_file = forms.FileField()


@admin.register(TemplateModel)
class TemplateAdmin(TemplateImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'enabled', 'has_errors', 'version', 'subject', 'updated_at')
    readonly_fields = ('name',)
    form = TemplateAdminForm
    fields = ('name', 'enabled', 'has_errors', 'layout', 'subject', 'body',)

    import_template_name = 'admin/happymailer/templatemodel/import.html'

    def get_model_info(self):
        opts = self.model._meta
        return (opts.app_label, opts.model_name,)

    def get_urls(self):
        urls = super(TemplateAdmin, self).get_urls()
        admin_view = self.admin_site.admin_view
        info = self.get_model_info()
        extras = [
            url(r'^preview/$', admin_view(self.preview_view), name='%s_%s_preview' % info),
            url(r'^send_test/$', admin_view(self.send_test_view), name='%s_%s_send_test' % info),
            url(r'^([^/]+)/version/([^/]+)/$', admin_view(self.history_view), name='%s_%s_version' % info),
            url(r'^export/$', admin_view(self.export_action), name='%s_%s_export' % info),
            url(r'^import/$', admin_view(self.import_action), name='%s_%s_import' % info),
        ]
        return extras + urls

    def export_action(self, request):
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=templatemodel_export.json'

        items = [{
            'name': t.name,
            'layout': t.layout,
            'subject': t.subject,
            'body': t.body,
            'version': t.version,
            'enabled': t.enabled,
            'has_errors': t.has_errors,
            'created_at': t.created_at,
            'updated_at': t.updated_at,
            'history': [{
                'layout': h.layout,
                'subject': h.subject,
                'body': h.body,
                'version': h.version,
                'archived_at': h.archived_at,
            } for h in t.history.all()]
        } for t in TemplateModel.objects.all()]

        json.dump(items, response, cls=DjangoJSONEncoder, indent=2, sort_keys=True)
        return response

    def import_action(self, request):
        context = {}
        form = ImportForm(request.POST or None, request.FILES or None)

        if request.POST and form.is_valid():
            import_file = form.cleaned_data['import_file']
            data = json.loads(import_file.read().decode('utf-8'))

            created_cnt = 0
            updated_cnt = 0
            with transaction.atomic():
                for item in data:
                    item_defaults = dict(**item)
                    del item_defaults['history']

                    template, created = TemplateModel.objects.get_or_create(
                        name=item['name'],
                        defaults=item_defaults)

                    if created:
                        created_cnt += 1
                        for h in item['history']:
                            template.history.create(**h)

                    else:
                        if item['version'] > template.version:
                            # to avoid post_save signal
                            TemplateModel.objects.filter(pk=template.pk).update(**item_defaults)
                            updated_cnt += 1

                            for h in item['history']:
                                if h['version'] > template.version:
                                    new_h = template.history.create(**h)
                                    new_h.archived_at = h['archived_at']
                                    new_h.save()

            messages.info(request, '%d templates added, %d templates updated' % (created_cnt, updated_cnt))

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)

        context.update(self.admin_site.each_context(request))

        context['form'] = form
        context['opts'] = self.model._meta

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name], context)

    def history_view(self, request, object_id, version):
        try:
            obj = HistoricalTemplate.objects.get(
                template=object_id,
                version=version,
            )
        except HistoricalTemplate.DoesNotExist:
            return Http404()

        return JsonResponse({
            'data': {
                'version': obj.version,
                'layout': obj.layout,
                'subject': obj.subject,
                'body': obj.body or '',
            }
        })

    def preview_view(self, request):
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

        try:
            compiled = tmpl.compile()
        except CompileError:
            return HttpResponseBadRequest()

        return JsonResponse({
            'html': compiled,
        })

    def send_test_view(self, request):
        form = FakedataForm(request.POST)
        if not form.is_valid():
            print('errors:', form.errors)
            return HttpResponseBadRequest()

        variables = json.loads(form.cleaned_data['variables'])
        template_cls = get_template(form.cleaned_data['template'])
        layout_cls = get_layout(form.cleaned_data['layout'])
        kwargs = fake.generate(template_cls.kwargs)

        recipient = '{} <{}>'.format(request.user.get_full_name(), request.user.email)
        tmpl = template_cls(recipient, _force_layout_cls=layout_cls, _force_variables=variables, **kwargs)
        tmpl.body = form.cleaned_data['body']
        tmpl.subject = "Test: {}".format(form.cleaned_data['subject'])
        tmpl.send(force=True)

        return JsonResponse({
            'mail': recipient,
        })

    def get_actions(self, request):
        return None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):

        if object_id:
            obj = self.get_object(request, admin.utils.unquote(object_id))

            ModelForm = self.get_form(request, obj)
            if request.method == 'POST':
                form = ModelForm(request.POST, request.FILES, instance=obj)
                if form.is_valid():
                    new_object = form.save()
                    return JsonResponse(dict(status='ok'))
                else:
                    return JsonResponse(dict(status='error', errors=form.errors))

            template = None
            for cls in template_classes:
                if cls.name == obj.name:
                    template = cls

            if not template:
                raise Http404()

            variables = template.fake_variables()

            def render_key(x, variables=None):
                if variables is None:
                    variables = {}

                if isinstance(x.trafaret, trafaret.Dict):
                    value = [ render_key(k, variables.get(x.name)) for k in x.trafaret.keys]
                else:
                    value = variables.get(x.name, fake.generate(x.trafaret))

                return {
                    'name': x.name,
                    'type': repr(x.trafaret),
                    'value': value,
                    'valueType': x.trafaret.__class__.__name__.lower()
                }


            history_options = [{
                'value': v.version,
                'label': '{version} (from {archived_at})'.format(
                    version=v.version, archived_at=v.archived_at.strftime('%Y-%m-%d %H:%M:%S'))}
                for v in obj.history.order_by('-version').all()]

            extra_context = dict(
                extra_context or {},
                happymailer_config=json.dumps({
                    'staticUrl': settings.STATIC_URL + 'happymailer/',
                    'template': {
                        'pk': obj.pk,
                        'template': obj.name,
                        'body': obj.body or '',
                        'layout': obj.layout or layout_classes[0].name,
                        'enabled': obj.enabled,
                        'subject': obj.subject or '',
                    },
                    'history': history_options,
                    'changelistUrl': reverse('admin:happymailer_templatemodel_changelist'),
                    'changeUrl': reverse('admin:happymailer_templatemodel_change', args=[obj.pk]),
                    'previewUrl': reverse('admin:happymailer_templatemodel_preview'),
                    'sendtestUrl': reverse('admin:happymailer_templatemodel_send_test'),
                    'layouts': [{'value': cls.name, 'label': cls.description or cls.name}
                                for cls in layout_classes],
                    'variables': [render_key(x, variables) for x in template.variables.keys],
                }).replace('<', '\\u003C'),
            )

        return super(TemplateAdmin, self).changeform_view(request, object_id, form_url, extra_context)
