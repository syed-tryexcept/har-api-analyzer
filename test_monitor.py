from monitor import parse_entries, safe_endpoint, short, to_int


def test_safe_endpoint_removes_query_string():
    url = "https://api.example.com/v1/items?token=SECRET&page=2"
    assert safe_endpoint(url) == "api.example.com/v1/items"


def test_safe_endpoint_removes_fragment():
    assert safe_endpoint("https://example.com/path#section") == "example.com/path"


def test_short_keeps_short_text_and_trims_long_text():
    assert short("abc", 10) == "abc"
    trimmed = short("x" * 100, 20)
    assert len(trimmed) == 20
    assert trimmed.startswith("...")


def test_to_int_handles_bad_values():
    assert to_int("200") == 200
    assert to_int(404) == 404
    assert to_int(None) == 0
    assert to_int("abc") == 0


def test_parse_entries_keeps_only_safe_fields():
    entries = [
        {
            "startedDateTime": "2026-10-29T05:33:43.689Z",
            "time": 268.212,
            "_resourceType": "fetch",
            "request": {
                "method": "PATCH",
                "url": "https://api.example.com/v1/items?token=SECRET",
                "headers": [{"name": "Authorization", "value": "Bearer SECRET"}],
            },
            "response": {"status": 200},
        }
    ]
    rows = parse_entries(entries)
    assert rows == [
        {
            "timestamp": "2026-10-29T05:33:43.689Z",
            "method": "PATCH",
            "endpoint": "api.example.com/v1/items",
            "status": 200,
            "duration_ms": 268.2,
            "resource_type": "fetch",
        }
    ]
    assert "SECRET" not in str(rows)


def test_parse_entries_handles_empty_and_missing_fields():
    assert parse_entries([]) == []
    rows = parse_entries([{}])
    assert rows[0]["status"] == 0
    assert rows[0]["endpoint"] == ""
