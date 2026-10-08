def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_upload_and_grounded_query(client):
    upload = client.post(
        "/v1/documents",
        files={
            "file": (
                "pv-ag.txt",
                b"Les travaux de toiture sont votes pour 12 000 euros avec ToitPro.",
                "text/plain",
            )
        },
    )
    assert upload.status_code == 201
    response = client.post(
        "/v1/query", json={"question": "Quels travaux de toiture ont ete votes ?"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["sources"][0]["filename"] == "pv-ag.txt"
    assert "[1]" in body["answer"]


def test_refuses_disguised_pdf(client):
    response = client.post(
        "/v1/documents",
        files={"file": ("attack.pdf", b"not a pdf", "application/pdf")},
    )
    assert response.status_code == 415


def test_refuses_path_and_extension(client):
    response = client.post(
        "/v1/documents",
        files={"file": ("../../payload.exe", b"x", "application/octet-stream")},
    )
    assert response.status_code == 415


def test_unknown_answer_has_no_sources(client):
    response = client.post("/v1/query", json={"question": "Quel est le nom du chat ?"})
    assert response.json()["grounded"] is False
