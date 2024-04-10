from __future__ import annotations

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from requests import Response

from fiddler.constants.common import CONTENT_TYPE_HEADER_KEY, MULTI_PART_CHUNK_SIZE
from fiddler.decorators import handle_api_error
from fiddler.entities.base import BaseEntity
from fiddler.entities.user import CreatedByMixin, UpdatedByMixin
from fiddler.schemas.file import FileResp
from fiddler.utils.logger import get_logger

logger = get_logger(__name__)


class File(BaseEntity, CreatedByMixin, UpdatedByMixin):
    def __init__(self, path: str | Path, name: str | None = None) -> None:
        """Construct a files instance."""
        self.path = path
        self.name = name or os.path.basename(self.path)
        self.id: UUID | None = None
        self.status: str | None = None
        self.type: str | None = None

        self.created_at: datetime | None = None
        self.updated_at: datetime | None = None

        # Deserialized response object
        self._resp: FileResp | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> File:
        """Build entity object from the given dictionary"""
        raise NotImplementedError()

    def _refresh(self, data: dict) -> None:
        """Refresh the fields of this instance from the given response dictionary"""
        resp_obj = FileResp(**data)

        # Reset fields
        self.name = resp_obj.name

        # Add remaining fields
        fields = [
            'id',
            'status',
            'type',
            'created_at',
            'updated_at',
        ]
        for field in fields:
            setattr(self, field, getattr(resp_obj, field, None))

        self._resp = resp_obj

    @handle_api_error
    def upload(
        self,
        chunk_size: int = MULTI_PART_CHUNK_SIZE,
    ) -> File:
        """Upload file. Single or multipart upload depends on file size"""
        if os.path.getsize(self.path) < chunk_size:
            return self.single_upload()

        return self.multipart_upload(chunk_size=chunk_size)

    @handle_api_error
    def single_upload(self) -> File:
        """Single part file upload"""

        response = self._client().post(
            url='/v3/files/upload',
            files={'file': (self.name, open(self.path, 'rb'))},
            headers={CONTENT_TYPE_HEADER_KEY: None},
        )

        self._refresh_from_response(response)
        return self

    @handle_api_error
    def multipart_upload(
        self,
        chunk_size: int = MULTI_PART_CHUNK_SIZE,
    ) -> File:
        """Multi part file upload"""

        # init multipart upload
        self._init_multipart_upload()

        assert self.id is not None
        # multipart parts upload
        parts = self._multipart_upload(
            chunk_size=chunk_size,
        )

        # multipart upload complete
        response = self._multipart_upload_complete(parts=parts)

        self._refresh_from_response(response)
        return self

    def _init_multipart_upload(self) -> File:
        logger.info('Multi-part upload initializing')
        response = self._client().post(
            url='/v3/files/multipart-init',
            data={'filename': self.name},
        )

        self._refresh_from_response(response)
        return self

    def _multipart_upload(self, chunk_size: int) -> list[dict[str, Any]]:
        parts: list[dict[str, Any]] = []
        part_number = 1

        with open(self.path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break

                logger.info('Uploading part %d', part_number)

                response = self._client().post(
                    url='/v3/files/multipart-upload',
                    files={
                        'file': (f'part_{part_number}_{self.name}', io.BytesIO(data)),
                        'file_id': (None, str(self.id)),
                        'part_number': (None, part_number),
                    },
                    headers={CONTENT_TYPE_HEADER_KEY: None},
                )

                parts.append(
                    {'number': part_number, 'id': response.json()['data']['part_id']}
                )

                part_number += 1

        return parts

    def _multipart_upload_complete(self, parts: list[dict[str, Any]]) -> Response:

        response = self._client().post(
            url='/v3/files/multipart-complete',
            json={
                'file_id': str(self.id),
                'parts': parts,
            },
        )

        logger.info('Multi-part upload complete')
        return response
