import time
import logging
from django.db.models.fields.related import ManyToOneRel, ManyToManyRel
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

_logger = logging.getLogger(__name__)


class Filter:

    query_relation_depth = 4

    LABEL_EXACT = _('Equals')
    LABEL_EXACT_NOT = _('Equals Not')
    LABEL_ICONTAINS = _('Contains')
    LABEL_ICONTAINS_NOT = _('Contains Not')
    LABEL_GTE = _('Greater or Equal')
    LABEL_LTE = _('Less or Equal')
    LABEL_TRUE = _('True')
    LABEL_FALSE = _('False')
    LABEL_SET = _('Is Set')
    LABEL_NOT_SET = _('Is Not Set')

    def __init__(
            self, model, query_relation_depth: int = 4,
            default_exclude: list[str] = None, default_filter_term: str = None
    ):
        self.model = model
        self.query_relation_depth = query_relation_depth
        self.default_exclude = default_exclude or ['tenant', 'user']
        self.default_filter_term = default_filter_term or ''
        self.fields = []
        self.field_paths = []

    @staticmethod
    def cast_decimal_places_to_step(decimal_places):
        if not decimal_places or decimal_places < 1:
            return '1'
        zero_count = decimal_places - 1
        return f'0.{"0" * zero_count}1'

    def get_fields(self, model_path: list, field_path: str):
        fields = self.get_local_fields(model_path[-1], field_path)
        if len(model_path) <= self.query_relation_depth:
            fields.extend(self.get_relation_fields(model_path, field_path))
        return sorted(fields, key=lambda x: x['label'].lower())

    def get_relation_fields(self, model_path, field_path):
        filter_exclude = getattr(model_path[-1], 'filter_exclude', [])
        filter_exclude.extend(self.default_exclude)
        fields = filter(
            lambda x: x.is_relation and x.name not in filter_exclude,
            model_path[-1]._meta.get_fields()
        )
        res = []
        for field in fields:
            if field.related_model in model_path:
                continue
            rel_path = f'{field_path}{"__" if field_path else ""}{field.name}'
            model_path_copy = model_path.copy()
            model_path_copy.append(field.related_model)
            try:
                label = field.verbose_name
            except AttributeError:
                label = field.related_model._meta.verbose_name
            res.append({
                'name': f'{rel_path}',
                'label': str(label),
                'type': field.get_internal_type(),
                'null': field.null,
                'choices': [],
                'fields': self.get_fields(model_path_copy, rel_path)
            })
        return res

    def get_local_fields(self, model, path):
        filter_exclude = getattr(model, 'filter_exclude', [])
        filter_exclude.extend(self.default_exclude)
        fields = filter(
            lambda x: not x.is_relation and x.name not in filter_exclude,
            model._meta.get_fields()
        )
        res = []
        for field in fields:
            field_path = f'{path}{"__" if path else ""}{field.name}'
            self.field_paths.append(field_path)
            step = (hasattr(field, 'decimal_places')
                    and self.cast_decimal_places_to_step(field.decimal_places)
                    or 1)
            res.append({
                'name': field_path,
                'label': str(field.verbose_name),
                'type': field.get_internal_type(),
                'choices': field.choices or [],
                'null': field.null,
                'step': step
            })
        if not hasattr(model, 'get_annotations'):
            return res
        for annotation in model.get_annotations():
            field_path = f'{path}{"__" if path else ""}{annotation["name"]}'
            self.field_paths.append(field_path)
            res.append({
                'name': field_path,
                'label': str(annotation['annotation'].verbose_name),
                'type': annotation['annotation'].field.__name__,
                'choices': [],
                'null': False,
                'step': getattr(annotation['annotation'], 'step', '1')
            })
        return res

    def to_html(self):
        key = f'filter-{self.model.__module__}.{self.model.__name__}-{get_language()}'
        html = cache.get(key)
        if html:
            return html
        if not self.fields:
            self.fields = self.get_fields([self.model], '')
        html = ''
        for f in self.fields:
            html += self.field_params(f)
        html = {
            'params': mark_safe(html.strip().replace('\n', '')),
            'field_paths': mark_safe(
                self.field_path_selection().strip().replace('\n', '')
            )
        }
        cache.set(key, html, 60 * 15)
        return {'params': html['params'], 'field_paths': html['field_paths']}

    def field_params(self, field):
        params = ''
        params += self.params(field)
        for f in field.get('fields', []):
            params += self.field_params(f)
        return f"""
            <div class="query-param" tabindex="-1" data-param="{field['name']}" data-param-label="{field['label']}">
                <p class="px-1 arrow">{field['label']}</p>
                <div class="query-params is-hidden" data-param="{field['name']}">
                    {params}
                </div>
            </div>
         """

    def field_map(self):
        return {
            'CharField': self.char_param,
            'TextField': self.char_param,
            'DecimalField': self.float_param,
            'FloatField': self.float_param,
            'BooleanField': self.bool_param,
            'IntegerField': self.int_param,
            'AutoField': self.int_param,
            'BigAutoField': self.int_param,
            'PositiveSmallIntegerField': self.int_param,
            'DateTimeField': self.date_time_param,
            'DateField': self.date_param,
            'ForeignKey': self.foreign_key_param
        }

    def parse_choices(self, choices):
        return ''.join([
            f'<option value="{choice[0]}">{choice[1]}</option>'
            for choice in choices
        ])

    def params(self, field):
        return self.field_map().get(field['type'], self.no_param)(field['name'], field)

    def param(
            self, key: str, value: dict, param: str, data_type: str,
            options: str, invert: bool = True
    ):

        def get_label(inverted=False):
            if param == 'exact':
                return self.LABEL_EXACT_NOT if inverted else self.LABEL_EXACT
            if param == 'icontains':
                return self.LABEL_ICONTAINS_NOT if inverted else self.LABEL_ICONTAINS
            if param == 'gte':
                return self.LABEL_GTE
            if param == 'lte':
                return self.LABEL_LTE

        def param_div(inverted=False):
            return f"""
                <div id="filter-id-{'~' if inverted else ''}{key}__{param}"
                     class="query-param" tabindex="-1" data-type="{data_type}"
                     data-step="{value.get('step', 1)}"
                     data-param="{param}" data-param-label="{value.get("label")}"
                >
                    <p class="px-1 arrowless">{get_label(inverted)}</p>
                    <div class="param-options is-hidden">
                        {options if options else ''}
                    </div>
                </div>
            """

        html = param_div()
        if invert:
            html += param_div(inverted=True)
        return html

    def char_param(self, key, value):
        if value.get('choices'):
            return self.char_choice_param(key, value)
        options = self.parse_choices(value.get('choices', ''))
        html = self.param(key, value, 'icontains', 'text', options)
        html += self.param(key, value, 'exact', 'text', options)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def char_choice_param(self, key, value):
        options = self.parse_choices(value.get('choices', []))
        html = self.param(key, value, 'exact', 'selection', options)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def float_param(self, key, value):
        options = self.parse_choices(value.get('choices', ''))
        html = self.param(key, value, 'exact', 'number', options)
        html += self.param(key, value, 'gte', 'number', options, False)
        html += self.param(key, value, 'lte', 'number', options, False)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def bool_param(self, key, value):
        options = self.parse_choices([('true', _('True')), ('false', _('False'))])
        html = self.param(key, value, 'exact', 'selection', options)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def int_param(self, key, value):
        options = self.parse_choices(value.get('choices', ''))
        html = self.param(key, value, 'exact', 'number', options)
        html += self.param(key, value, 'gte', 'number', options, False)
        html += self.param(key, value, 'lte', 'number', options, False)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def date_time_param(self, key, value):
        options = self.parse_choices(value.get('choices', ''))
        html = self.param(key, value, 'exact', 'datetime-local', options)
        html += self.param(key, value, 'gte', 'datetime-local', options, False)
        html += self.param(key, value, 'lte', 'datetime-local', options, False)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def date_param(self, key, value):
        options = self.parse_choices(value.get('choices', ''))
        html = self.param(key, value, 'exact', 'date', options)
        html += self.param(key, value, 'gte', 'date', options, False)
        html += self.param(key, value, 'lte', 'date', options, False)
        if value.get('null'):
            html += self.null_param(key, value)
        return html

    def foreign_key_param(self, key, value):
        if value.get('null'):
            return self.null_param(key, value)
        return ''

    def null_param(self, key, value):
        options = self.parse_choices([
            ('true', _('True')),
            ('false', _('False'))
        ])
        return f"""
            <div id="filter-id-~{key}__isnull"
                 class="query-param" tabindex="-1" data-type="selection"
                 data-param-invert="false"
                 data-param="isnull" data-param-label="{value.get("label")}"
            >
                <p class="px-1 arrowless">{self.LABEL_SET}</p>
                <div class="param-options is-hidden">
                    {options}
                </div>
            </div>
        """

    def no_param(self, key, value):
        return ''

    def field_path_selection(self):
        html = ''
        filter_exclude = getattr(self.model, 'filter_exclude', [])
        filter_exclude.extend(self.default_exclude)
        fields = [(x.verbose_name, x.name) for x in filter(
            lambda x:
            x.name not in filter_exclude
            and not isinstance(x, (ManyToOneRel, ManyToManyRel)),
            self.model._meta.get_fields()
        )]
        fields.extend([
            (x['annotation'].verbose_name, x['name'])
            for x in self.model.get_annotations()
        ])
        sorted_fields = sorted(fields, key=lambda x: x[0].lower())
        for field in sorted_fields:
            html += f"""
                <label class="checkbox is-unselectable my-1" style="width: 100%">
                    <input type="checkbox" name="{field[1]}" data-label="{field[0].lower()}">
                    <span>{field[0]}</span>
                </label>
            """
        return html
