import base64
import urllib.parse
from typing import Any

from amsdal_models.classes.model import Model
from amsdal_models.classes.utils import get_custom_properties

from amsdal_server.apps.common.serializers.fields_restriction import FieldsRestriction


class ObjectDataMixin:
    @classmethod
    def build_object_data(
        cls,
        item: Model,
        base_url: str,
        *,
        include_metadata: bool = False,
        fields_restrictions: dict[str, FieldsRestriction] | None = None,
        load_references: bool = False,
        is_file_object: bool = False,
    ) -> dict[str, Any]:
        if load_references:
            _item_data = item.model_dump()
        else:
            _item_data = item.model_dump_refs()

        _item_data = cls._encode_bytes(_item_data)

        for name in get_custom_properties(item.__class__):
            _item_data[name] = getattr(item, name)

        if include_metadata:
            _metadata = item.get_metadata().model_dump()
            _item_data['_metadata'] = _metadata

            metadata_restrictions = fields_restrictions.get('Metadata', None) if fields_restrictions else None
            if metadata_restrictions and metadata_restrictions.fields:
                new_metadata = {k: v for k, v in _metadata.items() if k in metadata_restrictions.fields}
                # we really want to filter ot fields if thy are valid
                if new_metadata:
                    _item_data['_metadata'] = new_metadata

            _item_data['_metadata']['lakehouse_address'] = urllib.parse.quote(item.get_metadata().address.to_string())
        else:
            _item_data.pop('_metadata', None)

        if is_file_object:
            _object_id = item.get_metadata().address.object_id
            _object_version = item.get_metadata().address.object_version
            _item_data['data'] = f'{base_url}api/objects/file-download/{_object_id}/?version_id={_object_version}'

        return _item_data

    @classmethod
    def _encode_bytes(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: cls._encode_bytes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls._encode_bytes(item) for item in data]
        elif isinstance(data, bytes | bytearray):
            return f'data:binary;base64, {base64.b64encode(data).decode("utf-8")}'
        return data
