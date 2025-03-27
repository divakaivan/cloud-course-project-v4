"""Test cases for `s3.delete_objects`."""

import boto3

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import object_exists_in_s3
from files_api.s3.write_objects import upload_s3_object
from tests.consts import TEST_BUCKET_NAME


# pylint: disable=unused-argument
def test__delete_existing_s3_object(mocked_aws: None):
    """Assert that an object can be deleted from S3."""
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=TEST_BUCKET_NAME, Key="test_file.txt", Body="test content"
    )
    delete_s3_object(TEST_BUCKET_NAME, "test_file.txt")
    assert not s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME).get("Contents")


# pylint: disable=unused-argument
def test__delete_nonexistent_s3_object(mocked_aws: None):
    """Assert that deleting a non-existent object does not raise an error."""
    s3_client = boto3.client("s3")
    delete_s3_object(TEST_BUCKET_NAME, "non_existent_file.txt")
    assert not s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME).get("Contents")
