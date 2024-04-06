import contextvars
import logging
import time
from django.apps import apps
from django.db.models import Q

_logger = logging.getLogger(__name__)

tenant_contextvar = contextvars.ContextVar('tenant', default=None)
member_contextvar = contextvars.ContextVar('member', default=None)


def set_tenant(tenant):
    tenant_contextvar.set(tenant)


def get_tenant():
    return tenant_contextvar.get()


def set_member(member):
    tenant = member.tenant if member is not None else None
    member_contextvar.set(member)
    tenant_contextvar.set(tenant)


def get_member():
    return member_contextvar.get()


class Unscoped:

    def __init__(self, tenant):
        self.tenant = tenant

    def __enter__(self):
        if self.tenant is None:
            _logger.warning(
                'Entering unscoped context manager with tenant already set to None!'
            )
        set_tenant(None)

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_tenant(self.tenant)


def unscoped():
    return Unscoped(get_tenant())


def per_tenant(include: Q = None, exclude: Q = None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            tenants = apps.get_model('accrete', 'Tenant').objects.all()
            if include is not None:
                tenants = tenants.filter(include)
            if exclude is not None:
                tenants = tenants.exclude(exclude)
            _logger.info(f'Running {f.__module__}.{f.__name__}')
            start_time = time.time()
            for tenant in tenants:
                set_tenant(tenant)
                f(*args, **kwargs)
            _logger.info(
                f'Finished {f.__module__}.{f.__name__} in {time.time() - start_time} seconds.'
            )
        return wrapper
    return decorator

