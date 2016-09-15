from django import forms

from .models import TemplateModel
from .utils import layout_classes, template_classes


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
    send_test = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(FakedataForm, self).__init__(*args, **kwargs)
        self.fields['layout'].choices = [(cls.name, cls.name) for cls in layout_classes]
        self.fields['template'].choices = [(cls.name, cls.name) for cls in template_classes]


class ImportForm(forms.Form):
    import_file = forms.FileField()