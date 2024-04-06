import logging
from django import template
from django.db.models import Manager
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from accrete.contrib.ui import TableField, TableFieldType

_logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag(name='combine_templates')
def combine_templates(template_name, request=None):
    html = ''
    for app in settings.INSTALLED_APPS:
        try:
            html += render_to_string(
                f'{app.split(".")[-1]}/{template_name}', request=request
            )
        except template.TemplateDoesNotExist:
            continue
    return mark_safe(html)


@register.filter(name='field_attr')
def get_attr_from_field(obj: object, field: TableField):

    def return_save(attr):
        if isinstance(attr, Manager):
            return attr.related_model
        if attr is None:
            return None
        if isinstance(attr, str):
            return attr
        return attr
    f_name = field.name
    if field.field_type == TableFieldType.CHOICE_DISPLAY:
        f_name = f'get_{f_name}_display'

    try:
        attribute = getattr(obj, f_name, False)
    except (AttributeError,):
        _logger.warning(f'Object {obj} has no attribute {f_name}')
        attribute = None
    return return_save(attribute)


@register.filter(name='get_attr')
def get_attr_from_string(param: object, value: str):

    def return_save(attr):
        if isinstance(attr, Manager):
            return attr.related_model
        if attr is None:
            return None
        if isinstance(attr, str):
            return attr
        return attr

    try:
        attribute = getattr(param, value, False)
    except (AttributeError,):
        _logger.warning(f'Object {param} has no attribute {value}')
        attribute = None
    return return_save(attribute)


@register.filter(name='related_obj_url')
def related_obj_url(param: object, value: str):
    attr = getattr(param, value, False)
    if attr and hasattr(attr, 'get_absolute_url'):
        return attr.get_absolute_url()
    return '#'


@register.filter(name='message_class')
def message_class(param):
    if param.level == 25:
        return 'is-success'
    if param.level == 30:
        return 'is-warning'
    if param.level == 40:
        return 'is-danger'
