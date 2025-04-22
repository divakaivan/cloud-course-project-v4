from fastapi.testclient import TestClient


def test_get_nonexistant_file(client: TestClient):
    response = client.get("/files/non_existent_file.txt")

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}


def test_delete_nonexistant_file(client: TestClient):
    response = client.delete("/files/non_existent_file.txt")

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}


def test_get_medata_nonexistant_file(client: TestClient):
    response = client.head("/files/non_existent_file.txt")

    assert response.status_code == 404
