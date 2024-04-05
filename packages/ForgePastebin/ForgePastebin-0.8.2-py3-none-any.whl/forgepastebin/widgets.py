import ew as ew_core
from ew import jinja2_ew as ew

from allura.lib.widgets import form_fields as ffw
from allura.lib.widgets import forms as f


class PasteEdit(ffw.AutoResizeTextarea):
    pass


class PasteLanguage(ew.SingleSelectField):

    def options(self):
        from pygments.lexers import get_all_lexers
        langs = sorted((item[0], item[1][0])
                        for item in get_all_lexers() if len(item[1]))
        options = [ew.Option(html_value='', label='<auto detect>')]
        options.extend([ew.Option(html_value=l[1], label=l[0])
                        for l in langs])
        return options


class PasteForm(f.ForgeForm):
    template='jinja:forgepastebin:templates/widgets/paste_form.html'
    @property
    def fields(self):
        fields = ew_core.NameList(super().fields)
        fields.append(PasteEdit(name='text',
            attrs={'style':'height:15em; width:745px; font-family:monospace'}))
        fields.append(PasteLanguage(name='lang'))
        fields.append(ew.Checkbox(name='private'))
        return fields

    def display_field_by_name(self, idx, value=None, ignore_errors=False):
        field = self.fields[idx]
        ctx = self.context_for(field)
        if value is not None:
            ctx['value'] = value
        display = field.display(**ctx)
        if ctx['errors'] and field.show_errors and not ignore_errors:
            display = "{}<div class='error'>{}</div>".format(display, ctx['errors'])
        return display
