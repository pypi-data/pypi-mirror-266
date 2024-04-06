from django.db.models import Model


def get_related_model(model: type[Model], rel_path: str) -> tuple[Model, list[str]]:
    names = []
    related_model = model
    for part in rel_path.split('__'):
        names.append(str(related_model._meta.verbose_name))
        try:
            next_model = related_model._meta.fields_map[part].related_model
            related_model = next_model
        except (AttributeError, KeyError):
            try:
                next_model = getattr(related_model, part).field.related_model
                if next_model is not None:
                    related_model = next_model
            except AttributeError:
                break
    return related_model, names
