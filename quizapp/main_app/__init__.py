from django import forms


class InlineFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(InlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            for name in form.fields:
                if name == 'DELETE':
                    form.fields[name].widget.attrs.update({'class': 'form-check-input'})
                else:
                    form.fields[name].widget.attrs.update(
                        {'placeholder': f'enter the {name.replace("_", " ")} here...'})
                    form.fields[name].widget.attrs.update({'class': 'form-control'})
