import botocore
import pytest
from fastapi import status
from fastapi.testclient import TestClient

TEST_FILE_PATH = "some/nested/file.txt"
TEST_FILE_CONTENT = b"some content"
TEST_FILE_CONTENT_TYPE = "text/plain"


def test__upload_file(client: TestClient):
    # create a file
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"New file uploaded at path: /{TEST_FILE_PATH}",
    }

    # update an existing file
    updated_content = b"updated content"
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, updated_content, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"Existing file updated at path: /{TEST_FILE_PATH}",
    }


def test__list_files_with_pagination(client: TestClient):
    # Upload multiple files
    for i in range(15):
        file_path = f"file_{i}.txt"
        client.put(
            f"/v1/files/{file_path}",
            files={"file": (file_path, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
        )

    # List some of the files with pagination
    response = client.get("/v1/files?page_size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 10
    assert "next_page_token" in data


def test__get_file_metadata(client: TestClient):
    client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )
    # Get file metadata
    response = client.head(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == 200
    headers = response.headers
    assert headers["Content-Type"] == TEST_FILE_CONTENT_TYPE
    assert headers["Content-Length"] == str(len(TEST_FILE_CONTENT))
    assert "Last-Modified" in headers


def test__get_file(client: TestClient):
    client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    response = client.get(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == TEST_FILE_CONTENT


def test__delete_file(client: TestClient):
    client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    response = client.delete(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
