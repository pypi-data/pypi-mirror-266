from django.db import models
from accrete.tenant import get_tenant
from accrete.annotation import AnnotationManagerMixin


class TenantManager(models.Manager, AnnotationManagerMixin):

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_tenant()
        if tenant:
            queryset = queryset.filter(tenant=tenant)
        return queryset.annotate(**self.get_annotations())

    def bulk_create(
            self,
            objs,
            batch_size=None,
            ignore_conflicts=False,
            update_conflicts=False,
            update_fields=None,
            unique_fields=None,
    ):
        tenant = get_tenant()
        if tenant is None and not all(obj.tenant_id for obj in objs):
            raise ValueError(
                'Tenant must be set for all objects when calling bulk_create'
            )
        for obj in objs:
            obj.tenant_id = tenant.pk
        return super().bulk_create(
            objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts, update_fields=update_fields,
            unique_fields=unique_fields
        )
