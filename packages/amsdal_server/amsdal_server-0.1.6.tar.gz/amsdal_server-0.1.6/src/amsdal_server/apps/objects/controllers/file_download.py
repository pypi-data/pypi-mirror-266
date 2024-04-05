from urllib.parse import quote

from amsdal_utils.models.enums import Versions
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response

from amsdal_server.apps.objects.router import router
from amsdal_server.apps.objects.services.file_object import ObjectFileApi


@router.get('/api/objects/file-download/{object_id}/')
async def file_download(
    object_id: str,
    request: Request,
    version_id: str = '',
) -> Response:
    file_obj = ObjectFileApi.get_file(
        request.user,
        object_id,
        version_id or Versions.LATEST,
    )

    if not file_obj:
        raise HTTPException(status_code=404, detail='File not found')

    return Response(
        content=file_obj.data,
        headers={
            'content-disposition': f'attachment; filename={quote(file_obj.filename)}',
        },
        media_type=file_obj.mimetype or 'application/octet-stream',
    )
