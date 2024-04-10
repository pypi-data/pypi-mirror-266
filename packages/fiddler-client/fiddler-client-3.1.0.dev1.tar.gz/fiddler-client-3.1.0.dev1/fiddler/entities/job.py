from __future__ import annotations

import time
from typing import Iterator
from uuid import UUID

from fiddler.configs import JOB_POLL_INTERVAL, JOB_WAIT_TIMEOUT
from fiddler.constants.job import JobStatus
from fiddler.decorators import handle_api_error
from fiddler.entities.base import BaseEntity
from fiddler.exceptions import AsyncJobFailed
from fiddler.schemas.job import JobResp
from fiddler.utils.logger import get_logger

logger = get_logger(__name__)


class Job(BaseEntity):  # pylint: disable=too-many-instance-attributes
    def __init__(self) -> None:
        """Construct a job instance"""
        self.name: str | None = None
        self.status: str | None = None
        self.progress: float | None = None
        self.info: dict | None = None
        self.error_message: str | None = None
        self.error_reason: str | None = None
        self.extras: dict | None = None

        self.id: UUID | None = None

        # Deserialized response object
        self._resp: JobResp | None = None

    @classmethod
    def _from_dict(cls, data: dict) -> Job:
        """Build entity object from the given dictionary"""

        # Deserialize the response
        resp_obj = JobResp(**data)

        # Initialize
        instance = cls()

        # Add remaining fields
        fields = [
            'id',
            'name',
            'progress',
            'status',
            'info',
            'error_message',
            'error_reason',
            'extras',
        ]
        for field in fields:
            setattr(instance, field, getattr(resp_obj, field, None))

        instance._resp = resp_obj

        return instance

    def _refresh(self, data: dict) -> None:
        """Refresh the fields of this instance from the given response dictionary"""
        # Deserialize the response
        resp_obj = JobResp(**data)

        # Add remaining fields
        fields = [
            'id',
            'name',
            'progress',
            'status',
            'info',
            'error_message',
            'error_reason',
            'extras',
        ]
        for field in fields:
            setattr(self, field, getattr(resp_obj, field, None))

        self._resp = resp_obj

    @staticmethod
    def _get_url(id_: UUID | str | None = None) -> str:
        """Get job resource/item url"""
        url = '/v3/jobs'
        return url if not id_ else f'{url}/{id_}'

    @classmethod
    @handle_api_error
    def get(cls, id_: UUID | str, verbose: bool = False) -> Job:
        """
        Get the job instance using job id

        :param id_: Unique identifier of the job
        :param verbose: flag to get extra details about the tasks executed
        :return: single job object for the input params
        """
        response = cls._client().get(
            url=cls._get_url(id_=id_), params={'verbose': verbose}
        )
        return cls._from_response(response=response)

    def watch(
        self, interval: int = JOB_POLL_INTERVAL, timeout: int = JOB_WAIT_TIMEOUT
    ) -> Iterator[Job]:
        """
        Watch job status at given interval and yield job object

        :param interval: Interval in seconds between polling for job status
        :param timeout: Timeout in seconds for iterator to stop.
        :return: Iterator of job objects
        """
        assert self.id is not None

        start_time = time.time()
        while True:
            try:
                response = self._client().get(url=self._get_url(id_=self.id))
                self._refresh_from_response(response)
            except ConnectionError:
                logger.exception(
                    'Failed to connect to the server. Retrying...\n'
                    'If this error persists, please reach out to Fiddler.'
                )
                continue

            yield self

            current_time = time.time()
            if (current_time - start_time) > timeout:
                raise TimeoutError(f'Timed out while watching job {self.id}')

            if self.status in [
                JobStatus.SUCCESS,
                JobStatus.FAILURE,
                JobStatus.REVOKED,
            ]:
                return

            time.sleep(interval)

    def wait(
        self, interval: int = JOB_POLL_INTERVAL, timeout: int = JOB_WAIT_TIMEOUT
    ) -> None:
        """
        Wait for job to complete either with success or failure status

        :param interval: Interval in seconds between polling for job status
        :param timeout: Timeout in seconds for iterator to stop.
        """
        log_prefix = f'{self.name}[{self.id}]'

        for job in self.watch(interval=interval, timeout=timeout):
            logger.info(
                '%s: status - %s, progress - %.2f%%',
                log_prefix,
                job.status,
                job.progress,
            )

            if job.status == JobStatus.SUCCESS:
                logger.info('%s: successfully completed', log_prefix)
            elif job.status == JobStatus.FAILURE:
                raise AsyncJobFailed(
                    f'{log_prefix} failed with {job.error_reason or "Exception"}: '
                    f'{job.error_message}'
                )
