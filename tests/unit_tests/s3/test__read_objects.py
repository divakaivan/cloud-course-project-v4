"""Test cases for `s3.read_objects`."""

import boto3

from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from tests.consts import TEST_BUCKET_NAME


# pylint: disable=unused-argument
def test__object_exists_in_s3(mocked_aws: None):
    """Assert that `object_exists_in_s3` returns the correct value when an object is or isn't present."""
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=TEST_BUCKET_NAME,
        Key="test_object.txt",
        Body="test data",
    )
    assert (
        object_exists_in_s3(bucket_name=TEST_BUCKET_NAME, object_key="test_object.txt")
        is True
    )
    assert (
        object_exists_in_s3(
            bucket_name=TEST_BUCKET_NAME, object_key="non_existent_object.txt"
        )
        is False
    )


# pylint: disable=unused-argument
def test__fetch_s3_object(mocked_aws: None):
    """Assert that `fetch_s3_object` returns the correct metadata."""
    s3_client = boto3.client("s3")
    test_data = "test data"
    s3_client.put_object(
        Bucket=TEST_BUCKET_NAME,
        Key="test_object.txt",
        Body=test_data,
    )
    response = fetch_s3_object(
        bucket_name=TEST_BUCKET_NAME, object_key="test_object.txt"
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert response["ContentLength"] == len(test_data)


# pylint: disable=unused-argument
def test__pagination(mocked_aws: None):
    """Assert that pagination works correctly."""
    s3_client = boto3.client("s3")
    for i in range(1, 6):
        s3_client.put_object(
            Bucket=TEST_BUCKET_NAME,
            Key=f"file{i}.txt",
            Body=f"content {i}",
        )

    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, max_keys=2)
    assert len(files) == 2
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(
        TEST_BUCKET_NAME, next_page_token, max_keys=2
    )
    assert len(files) == 2
    assert files[0]["Key"] == "file3.txt"
    assert files[1]["Key"] == "file4.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(
        TEST_BUCKET_NAME, next_page_token, max_keys=2
    )
    assert len(files) == 1
    assert files[0]["Key"] == "file5.txt"
    assert next_page_token is None


# pylint: disable=unused-argument
def test__mixed_page_sizes(mocked_aws: None):
    """Assert that pagination works correctly for pages of differing sizes."""
    s3_client = boto3.client("s3")
    for i in range(1, 6):
        s3_client.put_object(
            Bucket=TEST_BUCKET_NAME,
            Key=f"file{i}.txt",
            Body=f"content {i}",
        )

    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, max_keys=3)
    assert len(files) == 3
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"
    assert files[2]["Key"] == "file3.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(
        TEST_BUCKET_NAME, next_page_token, max_keys=1
    )
    assert len(files) == 1
    assert files[0]["Key"] == "file4.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(
        TEST_BUCKET_NAME, next_page_token, max_keys=2
    )
    assert len(files) == 1
    assert files[0]["Key"] == "file5.txt"
    assert next_page_token is None


# pylint: disable=unused-argument
def test__directory_queries(mocked_aws: None):
    """Assert that queries with prefixes work correctly with various directory prefixes on object keys."""

    test_objects = {
        "folder1/file1.txt": "content 1",
        "folder1/file2.txt": "content 2",
        "folder2/file3.txt": "content 3",
        "folder2/subfolder1/file4.txt": "content 4",
        "file5.txt": "content 5",
    }

    s3_client = boto3.client("s3")
    for key, content in test_objects.items():
        s3_client.put_object(
            Bucket=TEST_BUCKET_NAME,
            Key=key,
            Body=content,
        )

    # Query with prefix
    files, next_page_token = fetch_s3_objects_metadata(
        TEST_BUCKET_NAME, prefix="folder1/"
    )
    assert len(files) == 2
    assert files[0]["Key"] == "folder1/file1.txt"
    assert files[1]["Key"] == "folder1/file2.txt"
    assert next_page_token is None

    # Query with prefix for nested folder
    files, next_page_token = fetch_s3_objects_metadata(
        TEST_BUCKET_NAME, prefix="folder2/subfolder1/"
    )
    assert len(files) == 1
    assert files[0]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None

    # Query with no prefix
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME)
    assert len(files) == 5
    assert files[0]["Key"] == "file5.txt"
    assert files[1]["Key"] == "folder1/file1.txt"
    assert files[2]["Key"] == "folder1/file2.txt"
    assert files[3]["Key"] == "folder2/file3.txt"
    assert files[4]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None
