import logging
from uuid import uuid4
from django.db import transaction

_logger = logging.getLogger(__name__)


def save_form(form, reraise=False):
    form.is_saved = False
    form.save_error = None
    form.save_error_id = None
    try:
        if form.is_valid():
            with transaction.atomic():
                form.save()
            form.is_saved = True
    except Exception as e:
        form.save_error = repr(e)
        error_id = str(uuid4())[:8]
        _logger.exception(f'{error_id}: {e}')
        form.save_error_id = error_id
        if reraise:
            raise e
    return form
