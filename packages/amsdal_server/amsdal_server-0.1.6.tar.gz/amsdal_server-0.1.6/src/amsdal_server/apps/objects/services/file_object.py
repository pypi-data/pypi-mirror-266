from amsdal_models.classes.constants import FILE_CLASS_NAME
from amsdal_models.classes.model import Model
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS
from starlette.authentication import BaseUser

from amsdal_server.apps.classes.mixins.model_class_info import ModelClassMixin
from amsdal_server.apps.common.mixins.permissions_mixin import PermissionsMixin


class ObjectFileApi(PermissionsMixin, ModelClassMixin):
    @classmethod
    def get_file(cls, user: BaseUser, object_id: str, object_version: str) -> Model | None:
        model_class = cls.get_model_class_by_name(FILE_CLASS_NAME)
        permissions_info = cls.get_permissions_info(model_class, user)

        if not permissions_info.has_read_permission:
            return None

        qs = model_class.objects.filter(_address__object_id=object_id)

        if object_version:
            qs = qs.using(LAKEHOUSE_DB_ALIAS).filter(_address__object_version=object_version)

        return qs.get_or_none().execute()
