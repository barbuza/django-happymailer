import json

from django.conf import settings
from django.urls import re_path, path
from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.db import transaction
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.exceptions import TemplateSyntaxError
from django.template.response import TemplateResponse

from . import fake
from .backends.base import CompileError
from .forms import TemplateAdminForm, FakedataForm, ImportForm
from .models import TemplateModel, HistoricalTemplate
from .utils import layout_classes, template_classes, get_template, get_layout, render_react_key, template_compile_check


@admin.register(TemplateModel)
class TemplateAdmin(admin.ModelAdmin):
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
            path('preview/', admin_view(self.preview_action), name='%s_%s_preview' % info),
            re_path(r'^([^/]+)/version/([^/]+)/$', admin_view(self.version_action), name='%s_%s_version' % info),
            path('export/', admin_view(self.export_action), name='%s_%s_export' % info),
            path('import/', admin_view(self.import_action), name='%s_%s_import' % info),
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

                    template, created = TemplateModel.objects.update_or_create(
                        name=item['name'],
                        defaults=item_defaults,
                    )

                    if created:
                        created_cnt += 1
                    else:
                        updated_cnt += 1

                    template.history.all().delete()
                    for h in item['history']:
                        template.history.create(**h)

                    try:
                        template_cls = get_template(template.name)
                        template_compile_check(template_cls)
                    except CompileError as e:
                        messages.warning(request, '%s got compile error: %r' % (template.name, str(e)))

            messages.info(request, '%d templates added, %d templates updated' % (created_cnt, updated_cnt))

            url = reverse('admin:%s_%s_changelist' % self.get_model_info(),
                          current_app=self.admin_site.name)
            return HttpResponseRedirect(url)

        context.update(self.admin_site.each_context(request))

        context['form'] = form
        context['opts'] = self.model._meta

        # request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name], context)

    def version_action(self, request, object_id, version):
        try:
            obj = HistoricalTemplate.objects.get(
                template=object_id,
                version=version,
            )
        except HistoricalTemplate.DoesNotExist:
            return JsonResponse({'version': 'Unknown version'}, status=403)

        return JsonResponse({
            'data': {
                'version': obj.version,
                'layout': obj.layout,
                'subject': obj.subject,
                'body': obj.body or '',
            }
        })

    def preview_action(self, request):
        form = FakedataForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'form': form.errors}, status=400)

        variables = json.loads(form.cleaned_data['variables'])
        template_cls = get_template(form.cleaned_data['template'])
        layout_cls = get_layout(form.cleaned_data['layout'])
        kwargs = fake.generate(template_cls.kwargs)
        send_test = form.cleaned_data['send_test']

        recipient = '{} <{}>'.format(request.user.get_full_name(), request.user.email) if send_test else None

        tmpl = template_cls(recipient, _force_layout_cls=layout_cls, _force_variables=variables, **kwargs)
        tmpl.body = form.cleaned_data['body']
        tmpl.subject = "Test: {}".format(form.cleaned_data['subject'])

        try:
            compiled = tmpl.compile()
        except (CompileError, TemplateSyntaxError) as e:
            return JsonResponse({
                'template': str(e)
            }, status=400)

        if send_test:
            tmpl.send(force=True)

        return JsonResponse({
            'html': compiled,
            'email': recipient,
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
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'errors': form.errors})

            template = None
            for cls in template_classes:
                if cls.name == obj.name:
                    template = cls

            if not template:
                raise Http404()

            variables = template.fake_variables()

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
                    'layouts': [{'value': cls.name, 'label': cls.description or cls.name}
                                for cls in layout_classes],
                    'variables': [render_react_key(x, variables) for x in template.variables.keys],
                }).replace('<', '\\u003C'),
            )

        return super(TemplateAdmin, self).changeform_view(request, object_id, form_url, extra_context)
