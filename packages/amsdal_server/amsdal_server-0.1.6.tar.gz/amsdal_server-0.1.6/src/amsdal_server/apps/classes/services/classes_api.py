from amsdal.configs.main import settings
from amsdal.schemas.manager import SchemaManager
from amsdal_models.classes.constants import USER_MODELS_MODULE
from amsdal_models.classes.data_models.dependencies import DependencyModelNames
from amsdal_models.classes.manager import ClassManager
from amsdal_models.classes.model import Model
from amsdal_models.classes.utils import resolve_base_class_for_schema
from amsdal_models.classes.writer import ClassWriter
from amsdal_models.querysets.executor import LAKEHOUSE_DB_ALIAS
from amsdal_models.schemas.data_models.schema import ObjectSchema
from amsdal_models.schemas.data_models.schema import PropertyData
from amsdal_models.schemas.manager import BuildSchemasManager
from amsdal_utils.models.enums import SchemaTypes
from starlette.authentication import BaseUser

from amsdal_server.apps.classes.errors import ClassNotFoundError
from amsdal_server.apps.classes.mixins.column_info_mixin import ColumnInfoMixin
from amsdal_server.apps.classes.mixins.model_class_info import ModelClassMixin
from amsdal_server.apps.classes.serializers.class_info import ClassInfo
from amsdal_server.apps.classes.serializers.register_class import ClassSchema
from amsdal_server.apps.classes.serializers.register_class import RegisterClassData
from amsdal_server.apps.common.errors import AmsdalPermissionError
from amsdal_server.apps.common.mixins.permissions_mixin import PermissionsMixin
from amsdal_server.apps.common.permissions.enums import AccessTypes
from amsdal_server.apps.objects.mixins.object_data_mixin import ObjectDataMixin


class ClassesApi(PermissionsMixin, ModelClassMixin, ColumnInfoMixin, ObjectDataMixin):
    @classmethod
    def get_classes(cls, user: BaseUser) -> list[ClassInfo]:
        classes: list[Model] = cls.get_class_objects_qs().execute()
        class_metas: dict[str, Model] = {
            _item.object_id: _item for _item in cls.get_class_object_metas_qs(classes).execute()
        }
        result: list[ClassInfo] = []

        for class_item in classes:
            class_meta_item = class_metas[class_item.object_id]  # type: ignore[index]
            result.append(cls.get_class(user, class_item, class_meta_item))

        return result

    @classmethod
    def get_class_by_name(
        cls,
        user: BaseUser,
        class_name: str,
    ) -> ClassInfo:
        class_item: Model | None = cls.get_class_objects_qs().filter(_address__object_id=class_name).first().execute()

        if not class_item:
            msg = f'Class not found: {class_name}'
            raise ClassNotFoundError(class_name, msg)

        class_meta_item: Model = cls.get_class_object_metas_qs().get(_address__object_id=class_item.object_id).execute()

        return cls.get_class(user, class_item, class_meta_item)

    @classmethod
    def get_class(
        cls,
        user: BaseUser,
        class_item: Model,
        class_meta_item: Model,
    ) -> ClassInfo:
        model_class = cls.get_model_class(class_item)
        permissions_info = cls.get_permissions_info(model_class, user)
        class_properties = cls.get_class_properties_by_class_and_meta(class_item, class_meta_item)
        class_info = ClassInfo(
            **{  # type: ignore[arg-type]
                'class': class_item.object_id,
                'count': 0,
                'properties': class_properties,
            },
        )

        if permissions_info.has_read_permission:
            class_info.count = model_class.objects.latest().filter(_metadata__is_deleted=False).count().execute()

        return class_info

    @classmethod
    def register_class(
        cls,
        user: BaseUser,
        data: RegisterClassData,
        *,
        skip_data_migrations: bool = False,  # noqa: ARG003
    ) -> ClassInfo:
        from models.core.class_object import ClassObject  # type: ignore[import-not-found]

        permissions_info = cls.get_permissions_info(
            ClassObject,
            user,
            [AccessTypes.CREATE, AccessTypes.UPDATE],
        )
        object_schema = cls._build_object_schema(data.class_schema)

        model_object = (
            ClassObject.objects.using(LAKEHOUSE_DB_ALIAS)
            .latest()
            .filter(
                _metadata__is_deleted=False,
                title=data.class_schema.title,
            )
            .first()
            .execute()
        )

        if model_object:
            if not permissions_info.has_update_permission:
                raise AmsdalPermissionError(
                    access_type=AccessTypes.UPDATE,
                    class_name=ClassObject.__name__,
                )
        elif not permissions_info.has_create_permission:
            raise AmsdalPermissionError(
                access_type=AccessTypes.CREATE,
                class_name=ClassObject.__name__,
            )

        cls._generate_model_class(object_schema)

        class_properties = cls.get_class_properties(object_schema)
        class_info = ClassInfo(
            **{  # type: ignore[arg-type]
                'class': object_schema.title,
                'count': 0,  # TODO: get count
                'properties': class_properties,
            },
        )

        return class_info

    @classmethod
    def unregister_class(
        cls,
        user: BaseUser,
        class_name: str,
    ) -> None:
        from models.core.class_object import ClassObject

        permissions_info = cls.get_permissions_info(
            ClassObject,
            user,
            [AccessTypes.DELETE],
        )

        if not permissions_info.has_update_permission:
            raise AmsdalPermissionError(
                access_type=AccessTypes.DELETE,
                class_name=ClassObject.__name__,
            )

        class_object = (
            ClassObject.objects.latest()
            .filter(
                title=class_name,
                _metadata__is_deleted=False,
            )
            .first()
            .execute()
        )

        if class_object:
            class_object.get_metadata().is_deleted = True
            class_object.save()

    @classmethod
    def _build_object_schema(cls, class_schema: ClassSchema) -> ObjectSchema:
        return ObjectSchema(  # type: ignore[call-arg]
            title=class_schema.title,
            type=class_schema.type,
            properties={
                property_name: PropertyData(**property_data.model_dump())
                for property_name, property_data in class_schema.properties.items()
            },
            required=class_schema.required,
            indexed=class_schema.indexed,
            unique=class_schema.unique,
            custom_code=class_schema.custom_code,
        )

    @classmethod
    def _generate_model_class(cls, schema: ObjectSchema) -> None:
        model_names = DependencyModelNames.build_from_database()
        class_writer = ClassWriter(settings.models_root_path)
        class_writer.generate_model(
            schema=schema,
            schema_type=SchemaTypes.USER,
            base_class=resolve_base_class_for_schema(schema),
            model_names=model_names,
            sub_models_directory=USER_MODELS_MODULE,
        )

        class_manager = ClassManager()
        class_manager.init_models_root(settings.models_root_path)
        class_manager.unload_classes(schema.title, SchemaTypes.USER)
        BuildSchemasManager.add_user_schema(settings.schemas_root_path, schema)
        schema_manager = SchemaManager()
        schema_manager.invalidate_user_schemas()
