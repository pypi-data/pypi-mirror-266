import logging
import json
import operator
from django.db.models import Model, Q, QuerySet
from accrete.utils.models import get_related_model
from accrete.annotation import Annotation

_logger = logging.getLogger(__name__)

Querystring_KEY_MAP = {
    'querystring': 'q',
    'order': 'order',
    'paginate_by': 'paginate_by',
    'page': 'page'
}


def filter_from_querystring(
        model: type[Model], get_params: dict, key_map: dict = None
) -> QuerySet:

    key_map = key_map or Querystring_KEY_MAP
    querystring = get_params.get(key_map['querystring'], '[]')
    order = get_params.get(key_map['order']) or model._meta.ordering

    return model.objects.filter(
        parse_querystring(model, querystring)
    ).order_by(*order).distinct()


def parse_querystring(model: type[Model], query_string: str) -> Q:
    """
    param: query_string: JSON serializable string
    [{term: value}, '&', [{term: value}, '|', {~term: value}]]
    Q(term=value) & (Q(term=value) | ~Q(term=value))
    """

    def get_expression(term: str, value) -> Q:
        invert = False
        if term.startswith('~'):
            invert = True
            term = term[1:]

        parts = term.split('__')
        if len(parts) == 1:
            expression = Q(**{term: value})
            return ~expression if invert else expression

        rel_path = '__'.join(parts[:-2])
        related_model, x = get_related_model(model, rel_path)
        attr = getattr(related_model, parts[-2])
        if not isinstance(attr, Annotation):
            expression = Q(**{term: value})
            return ~expression if invert else expression

        objects = related_model.objects.filter(Q(**{
            '__'.join(parts[-2:]): value
        }))
        expression = Q(**{
            f'{rel_path}{"__" if rel_path else ""}id__in':
                objects.values_list('id', flat=True)
        })

        return ~expression if invert else expression

    def parse_query_block(sub_item) -> Q:
        op = ops['&']
        parsed_query = Q()
        for item in sub_item:
            if isinstance(item, list):
                parsed_query = op(parsed_query, parse_query_block(item))
                op = ops['&']
            elif isinstance(item, dict):
                dict_query = Q()
                for term, value in item.items():
                    dict_query = ops['&'](dict_query, get_expression(term, value))
                parsed_query = op(parsed_query, dict_query)
            elif isinstance(item, str):
                if item not in '&|^':
                    raise ValueError(
                        f'Invalid operator in querystring: {item}.'
                        f'Operator must be one of &, |, ^'
                    )
                op = ops[item]

            else:
                raise ValueError(
                    f'Unsupported item in querystring: {item}.'
                    f'Item must be an instance of list, dict or str'
                )
        return parsed_query

    query_data = json.loads(query_string.strip('?&='))
    if isinstance(query_data, dict):
        query_data = [query_data]

    ops = {'&': operator.and_, '|': operator.or_, '^': operator.xor}
    query = parse_query_block(query_data)
    return query