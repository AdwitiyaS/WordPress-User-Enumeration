import responses
from wp_vuln_tool.enum_rest_api import enumerate_rest_api


@responses.activate
def test_rest_api_exposed():
    responses.add(
        responses.GET,
        "http://localhost:8080/wp-json/wp/v2/users",
        json=[{"id": 1, "slug": "admin", "name": "Admin"}],
        status=200,
    )
    result = enumerate_rest_api("http://localhost:8080")
    assert result["success"] is True
    assert result["users"][0]["username"] == "admin"


@responses.activate
def test_rest_api_not_exposed():
    responses.add(
        responses.GET,
        "http://localhost:8080/wp-json/wp/v2/users",
        status=404,
    )
    result = enumerate_rest_api("http://localhost:8080")
    assert result["success"] is False