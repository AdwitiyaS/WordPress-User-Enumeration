import responses
from wp_vuln_tool.enum_author_archive import enumerate_author_archive


@responses.activate
def test_author_archive_redirect():
    responses.add(
        responses.GET,
        "http://localhost:8080/?author=1",
        status=301,
        headers={"Location": "http://localhost:8080/author/admin/"},
    )
    for i in range(2, 11):
        responses.add(responses.GET, f"http://localhost:8080/?author={i}", status=404)

    result = enumerate_author_archive("http://localhost:8080", max_id=10)
    assert result["success"] is True
    assert result["users"][0]["username"] == "admin"