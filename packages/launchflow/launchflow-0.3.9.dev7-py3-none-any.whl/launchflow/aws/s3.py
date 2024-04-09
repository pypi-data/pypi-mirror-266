import io
from typing import IO

try:
    import boto3
except ImportError:
    boto3 = None


from typing import Union

from launchflow.resource import Resource
from pydantic import BaseModel


class S3BucketConnectionInfo(BaseModel):
    bucket_name: str


class S3Bucket(Resource[S3BucketConnectionInfo]):
    """A S3 Bucket resource.

    **Attributes**:
    - `name` (str): The name of the bucket. This must be globally unique.
    - `region` (str): The region of the bucket. Defaults to the environment default.

    Example usage:
    ```python
    import launchflow as lf
    bucket = lf.aws.S3Bucket("my-bucket")
    bucket.blob("my-file").upload_from_filename("my-file")
    ```
    """

    def __init__(self, name: str, *, region=None) -> None:
        super().__init__(
            name=name,
            product_name="aws_s3_bucket",
            create_args={"region": region},
        )
        # public metadata
        self.region = region

    def bucket(self):
        """Get the AWS bucket resource returned by the boto3 library.

        **Returns**:
        - The [AWS bucket object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/bucket/index.html) from the boto3 library.
        """
        if boto3 is None:
            raise ImportError(
                "boto3 not found. "
                "You can install it with pip install launchflow[aws]"
            )
        connection_info = self.connect()
        return boto3.resource("s3").Bucket(connection_info.bucket_name)

    def upload_file(self, to_upload: Union[str, IO], bucket_path: str):
        """Uploads a file to the S3 bucket.

        Args:
        - `to_upload` (Union[str, IO]): The file to upload. This can be a string representing the path to the file, or a file-like object.
        - `bucket_path` (str): The path to upload the file to in the bucket.

        Example usage:
        ```python
        import launchflow as lf
        bucket = lf.aws.S3Bucket("my-bucket")
        bucket.upload_file("my-file.txt", "my-file.txt")
        bucket.upload_file(open("my-file.txt", "r"), "my-file.txt")
        ```
        """
        bucket = self.bucket()
        if isinstance(to_upload, str):
            bucket.upload_file(to_upload, bucket_path)
        else:
            bucket.upload_fileobj(to_upload, bucket_path)

    def upload_from_string(self, to_upload: str, bucket_path: str):
        """Uploads a string to the S3 bucket.

        Args:
        - `to_upload` (str): The string to upload.
        - `bucket_path` (str): The path to upload the string to in the bucket.

        Example usage:
        ```python
        import launchflow as lf

        bucket = lf.aws.S3Bucket("my-bucket")
        bucket.upload_from_string("hello", "hello.txt")
        ```
        """
        to_write = io.BytesIO(to_upload.encode("utf-8"))
        return self.upload_file(to_write, bucket_path)

    def download_file(self, bucket_path: str):
        """Downloads a file from the S3 bucket.

        Args:
        - `bucket_path` (str): The path to the file in the bucket.

        Example usage:
        ```python
        import launchflow as lf
        bucket = lf.aws.S3Bucket("my-bucket")
        with open("my-file.txt", "w") as f:
            f.write(bucket.download_file("my-file.txt"))
        ```
        """
        bucket = self.bucket()
        bytes_io = io.BytesIO()
        bucket.download_fileobj(bucket_path, bytes_io)
        bytes_io.seek(0)
        return bytes_io.read()
