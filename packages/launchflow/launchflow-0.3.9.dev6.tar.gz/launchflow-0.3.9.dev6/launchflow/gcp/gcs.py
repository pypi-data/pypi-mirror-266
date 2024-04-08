import io
from typing import IO

try:
    from google.cloud import storage
except ImportError:
    storage = None


from typing import Union

from launchflow.resource import Resource
from pydantic import BaseModel


class GCSBucketConnectionInfo(BaseModel):
    bucket_name: str


class GCSBucket(Resource[GCSBucketConnectionInfo]):
    """A GCS Bucket resource.

    **Attributes**:
    - `name` (str): The name of the bucket. This must be globally unique.
    - `location` (str): The location of the bucket. Defaults to "US".

    Example usage:
    ```python
    import launchflow as lf

    bucket = lf.gcp.GCSBucket("my-bucket")
    bucket.blob("my-file").upload_from_filename("my-file")
    ```
    """

    def __init__(self, name: str, *, location="US") -> None:
        super().__init__(
            name=name,
            product_name="gcp_storage_bucket",
            create_args={"location": location},
        )
        # public metadata
        self.location = location

    def bucket(self):
        """Get the GCS bucket object returned by the google-cloud-storage library.

        **Returns**:
        - The [GCS bucket object](https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.bucket.Bucket) from the GCS client library.
        """
        if storage is None:
            raise ImportError(
                "google-cloud-storage not found. "
                "You can install it with pip install launchflow[gcp]"
            )
        connection_info = self.connect()
        return storage.Client().get_bucket(connection_info.bucket_name)

    def upload_file(self, to_upload: Union[str, IO], bucket_path: str):
        """Uploads a file to the GCS bucket.

        Args:
        - `to_upload` (Union[str, IO]): The file to upload. This can be a string representing the path to the file, or a file-like object.
        - `bucket_path` (str): The path to upload the file to in the bucket.

        Example usage:

        ```python
        import launchflow as lf

        bucket = lf.gcp.GCSBucket("my-bucket")
        bucket.upload_file("my-file.txt", "my-file.txt")
        bucket.upload_file(open("my-file.txt", "r"), "my-file.txt")
        ```
        """
        bucket = self.bucket()
        if isinstance(to_upload, str):
            bucket.blob(bucket_path).upload_from_filename(to_upload)
        else:
            bucket.blob(bucket_path).upload_from_file(to_upload)

    def upload_from_string(self, to_upload: str, bucket_path: str):
        """Uploads a string to the GCS bucket.

        Args:
        - `to_upload` (str): The string to upload.
        - `bucket_path` (str): The path to upload the string to in the bucket.

        Example usage:
        ```python
        import launchflow as lf

        bucket = lf.gcp.GCSBucket("my-bucket")
        bucket.upload_from_string("hello", "hello.txt")
        ```
        """
        to_write = io.BytesIO(to_upload.encode("utf-8"))
        return self.upload_file(to_write, bucket_path)

    def download_file(self, bucket_path: str):
        """Downloads a file from the GCS bucket.

        Args:
        - `bucket_path` (str): The path to the file in the bucket.

        Example usage:
        ```python
        import launchflow as lf

        bucket = lf.gcp.GCSBucket("my-bucket")
        with open("my-file.txt", "w") as f:
            f.write(bucket.download_file("my-file.txt"))
        ```
        """
        bucket = self.bucket()
        return bucket.blob(bucket_path).download_as_bytes()
