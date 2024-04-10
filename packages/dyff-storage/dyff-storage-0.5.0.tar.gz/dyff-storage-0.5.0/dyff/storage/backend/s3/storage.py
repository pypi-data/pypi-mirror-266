# SPDX-FileCopyrightText: 2024 UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import io

# mypy: disable-error-code="import-untyped"
from datetime import datetime, timedelta
from pathlib import Path
from typing import BinaryIO, Iterable, Optional, Tuple
from urllib.parse import urlparse

import minio
import minio.api
import minio.helpers
import minio.time

from dyff.schema.dataset import max_artifact_size_bytes
from dyff.schema.platform import Artifact, StorageSignedURL
from dyff.storage import paths
from dyff.storage.backend.base.storage import StorageBackend
from dyff.storage.config import config


class _MyMinio(minio.Minio):
    def presigned_url_for_base(
        self,
        base_url: str,
        method: str,
        bucket_name: str,
        object_name: str,
        expires: timedelta = timedelta(days=7),
        response_headers: minio.helpers.DictType | None = None,
        request_date: datetime | None = None,
        version_id: str | None = None,
        extra_query_params: minio.helpers.DictType | None = None,
    ) -> str:
        """Get presigned URL of an object relative to an arbitrary base URL, for HTTP
        method, expiry time and custom request parameters.

        The base URL can contain a "netloc" and an optional scheme. If a scheme
        is provided, it must be either 'http' or 'https'.

        :param base_url: The base URL where the client will access the s3
            system. Examples: ``s3.some.domain:9000``, ``https://other.domain``.
        :param method: HTTP method.
        :param bucket_name: Name of the bucket.
        :param object_name: Object name in the bucket.
        :param expires: Expiry in seconds; defaults to 7 days.
        :param response_headers: Optional response_headers argument to
                                 specify response fields like date, size,
                                 type of file, data about server, etc.
        :param request_date: Optional request_date argument to
                             specify a different request date. Default is
                             current date.
        :param version_id: Version ID of the object.
        :param extra_query_params: Extra query parameters for advanced usage.
        :return: URL string.

        Example::
            # Get presigned URL string to PUT 'my-object' in
            # 'my-bucket' with one day expiry, where the client
            # will access the s3 system at 'https://s3.mysite.com'.
            url = client.presigned_url_for_base(
                "https://s3.mysite.com",
                "PUT",
                "my-bucket",
                "my-object",
                expires=timedelta(days=1),
            )
            print(url)
        """
        # Same as get_presigned_url(), except we modify the URL before signing

        minio.api.check_bucket_name(bucket_name, s3_check=self._base_url.is_aws_host)
        minio.api.check_non_empty_string(object_name)
        if expires.total_seconds() < 1 or expires.total_seconds() > 604800:
            raise ValueError("expires must be between 1 second to 7 days")

        region = self._get_region(bucket_name)
        query_params = extra_query_params or {}
        query_params.update({"versionId": version_id} if version_id else {})
        query_params.update(response_headers or {})
        creds = self._provider.retrieve() if self._provider else None
        if creds and creds.session_token:
            query_params["X-Amz-Security-Token"] = creds.session_token
        url = self._base_url.build(
            method,
            region,
            bucket_name=bucket_name,
            object_name=object_name,
            query_params=query_params,
        )

        # Modify the URL
        parsed_base_url = urlparse(base_url)
        if not parsed_base_url.netloc:
            parsed_base_url = urlparse(f"https://{base_url}")
        if any(
            [
                parsed_base_url.path,
                parsed_base_url.query,
                parsed_base_url.params,
                parsed_base_url.fragment,
            ]
        ):
            raise ValueError(
                f"'base_url' must be only 'scheme://netloc' ; got {base_url}"
            )
        url = minio.helpers.url_replace(
            url, scheme=parsed_base_url.scheme, netloc=parsed_base_url.netloc
        )

        if creds:
            url = minio.api.presign_v4(
                method,
                url,
                region,
                creds,
                request_date or minio.time.utcnow(),
                int(expires.total_seconds()),
            )
        return minio.api.urlunsplit(url)


def _bucket_name_from_path(path: str) -> str:
    return _split_bucket_path(path)[0]


def _drop_protocol(path: str) -> str:
    protocol = "s3://"
    if path.startswith(protocol):
        path = path[len(protocol) :]
    return path


def _split_bucket_path(path: str) -> Tuple[str, str]:
    path = _drop_protocol(path)
    parts = path.split("/")
    return parts[0], "/".join(parts[1:])


def _configured_internal_endpoint() -> str:
    if config.storage.s3.internal_endpoint is not None:
        return config.storage.s3.internal_endpoint
    else:
        return config.storage.s3.endpoint


def _get_client() -> _MyMinio:
    endpoint = _configured_internal_endpoint()
    parsed_endpoint = urlparse(endpoint, scheme="https")
    if parsed_endpoint.scheme == "http":
        secure = False
    else:
        secure = True
    parsed_endpoint = parsed_endpoint._replace(scheme="")
    return _MyMinio(
        # Minio doesn't allow paths in the URL
        endpoint=parsed_endpoint.netloc,
        access_key=config.storage.s3.access_key,
        secret_key=config.storage.s3.secret_key.get_secret_value(),
        secure=secure,
    )


class S3StorageBackend(StorageBackend):
    def storage_size(self, path: str) -> int:
        bucket, prefix = _split_bucket_path(path)
        client = _get_client()
        objects = client.list_objects(bucket, prefix, recursive=True)
        return sum(obj.size for obj in objects)

    def list_dir(self, path: str, *, recursive: bool = False) -> Iterable[str]:
        if not path.startswith("s3://"):
            raise ValueError("path must be an s3 object")
        if not path.endswith("/"):
            path += "/"
        client = _get_client()
        remote_path = path[len("s3://") :]
        bucket_name, *rest = remote_path.split("/")
        prefix = "/".join(rest)
        objects = client.list_objects(bucket_name, prefix, recursive=recursive)
        yield from (f"s3://{obj.bucket_name}/{obj.object_name}" for obj in objects)

    def download_recursive(self, source: str, destination: str) -> None:
        if not source.startswith("s3://"):
            raise ValueError("source must be an s3 object")
        if not source.endswith("/"):
            source += "/"
        client = _get_client()
        remote_path = source[len("s3://") :]
        bucket_name, *rest = remote_path.split("/")
        prefix = "/".join(rest)
        objects = client.list_objects(bucket_name, prefix, recursive=True)

        for obj in objects:
            if obj.object_name.endswith("/"):
                # Not a file
                continue
            remote_file = Path(obj.object_name).relative_to(prefix)
            remote_directory = Path(obj.object_name).parent.relative_to(prefix)
            local_directory = Path(destination) / remote_directory
            local_directory.mkdir(parents=True, exist_ok=True)
            local_file = Path(destination) / remote_file
            client.fget_object(obj.bucket_name, obj.object_name, str(local_file))

    def upload_recursive(self, source: str, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        if not destination.endswith("/"):
            destination += "/"

        source_path = Path(source)
        if not source_path.is_dir():
            raise ValueError("source must be a local directory")

        client = _get_client()
        bucket_name, bucket_path = _split_bucket_path(destination)

        source_paths = [path for path in source_path.rglob("*") if path.is_file()]
        relative_paths = [path.relative_to(source) for path in source_paths]

        if bucket_path != "":
            assert bucket_path[-1] == "/"  # See above
            prefix = bucket_path
        else:
            prefix = ""

        for file_path, upload_location in zip(source_paths, relative_paths):
            client.fput_object(
                bucket_name, f"{prefix}{upload_location}", str(file_path)
            )

    def put_object(self, data: bytes | BinaryIO, destination: str) -> None:
        if not destination.startswith("s3://"):
            raise ValueError("destination must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(destination)
        if bucket_path.endswith("/"):
            raise ValueError("destination is a directory")
        if isinstance(data, bytes):
            data = io.BytesIO(data)
        _get_client().put_object(
            bucket_name, bucket_path, data, length=-1, part_size=10 * 1024 * 1024
        )

    def get_object(self, source: str) -> BinaryIO:
        if not source.startswith("s3://"):
            raise ValueError("source must be an s3 object")
        bucket_name, bucket_path = _split_bucket_path(source)
        if bucket_path.endswith("/"):
            raise ValueError("source is a directory")

        try:
            response = _get_client().get_object(bucket_name, bucket_path)
            return io.BytesIO(response.data)
        finally:
            response.close()
            response.release_conn()

    def signed_url_for_artifact_upload(
        self,
        artifact: Artifact,
        storage_path: str,
        *,
        size_limit_bytes: Optional[int] = None,
        _internal_client: bool = False,
    ) -> StorageSignedURL:
        """Create a temporary signed URL that can be used in a PUT request to upload an
        ``Artifact`` directly to storage."""
        if size_limit_bytes is None:
            size_limit_bytes = max_artifact_size_bytes()
        if artifact.digest.md5 is None:
            raise ValueError("requires artifact.digest.md5")
        bucket_name, bucket_path = _split_bucket_path(storage_path)
        client = _get_client()

        # If the s3 provider is self-hosted (e.g. Minio), external clients
        # connect to it at a different URL than internal clients. We must sign
        # the correct URL, depending on which kind of client will use it.
        if _internal_client and config.storage.s3.internal_endpoint is not None:
            configured_url = config.storage.s3.internal_endpoint
        else:
            configured_url = config.storage.s3.endpoint

        signed_url = client.presigned_url_for_base(
            configured_url,
            "PUT",
            bucket_name,
            f"{bucket_path}/{artifact.path}",
            expires=timedelta(hours=1),
        )

        headers: dict[str, str] = {
            # TODO: Is there an s3 equivalent of this?
            # Google custom header limiting the size of the artifact
            # "x-goog-content-length-range": f"0,{size_limit_bytes}",
        }
        return StorageSignedURL(url=signed_url, method="PUT", headers=headers)

    def signed_url_for_dataset_upload(
        self,
        dataset_id: str,
        artifact: Artifact,
        *,
        size_limit_bytes: Optional[int] = None,
        storage_path: Optional[str] = None,
        _internal_client: bool = False,
    ) -> StorageSignedURL:
        storage_path = storage_path or paths.dataset_root(dataset_id)
        return self.signed_url_for_artifact_upload(
            artifact,
            storage_path,
            size_limit_bytes=size_limit_bytes,
            _internal_client=_internal_client,
        )

    def object_md5hash(self, storage_path: str) -> bytes:
        bucket_name, bucket_path = _split_bucket_path(storage_path)
        client = _get_client()

        response = None
        try:
            response = client.get_object(bucket_name, bucket_path)
            if response is None:
                raise ValueError(f"no object {storage_path}")
            # FIXME: This is potentially a very expensive operation. We have to
            # compute it on the server for security, but we should cache it in
            # the object metadata if we can confirm that users can't alter the
            # metadata using the signed upload URLs.
            # Also consider the s3 mechanisms for pre-computing digests as
            # metadata (but note that it doesn't support md5):
            # https://aws.amazon.com/blogs/aws/new-additional-checksum-algorithms-for-amazon-s3/
            return hashlib.md5(response.read()).digest()
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def dataset_artifact_md5hash(
        self, dataset_id: str, artifact_path: str, *, storage_path: Optional[str] = None
    ) -> bytes:
        storage_path = storage_path or paths.dataset_root(dataset_id)
        return self.object_md5hash(f"{storage_path}/{dataset_id}/{artifact_path}")


__all__ = ["S3StorageBackend"]
