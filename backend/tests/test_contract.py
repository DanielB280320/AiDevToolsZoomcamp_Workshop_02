"""Checks the running API against the contract in the repository-root openapi.yaml."""

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from app.main import app

SPEC = yaml.safe_load((Path(__file__).resolve().parents[2] / "openapi.yaml").read_text())
REGISTRY = Registry().with_resource("urn:kickboard", Resource.from_contents(SPEC, default_specification=DRAFT202012))
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


def assert_matches_schema(name, instance):
    validator = Draft202012Validator(
        {"$ref": f"urn:kickboard#/components/schemas/{name}"}, registry=REGISTRY, format_checker=FormatChecker()
    )
    errors = [f"{list(e.absolute_path)}: {e.message}" for e in validator.iter_errors(instance)]
    assert not errors, f"{name} does not match openapi.yaml:\n" + "\n".join(errors[:5])


def operations(paths):
    return {(method, path) for path, item in paths.items() for method in item if method in HTTP_METHODS}


def test_implements_exactly_the_documented_operations():
    assert operations(app.openapi()["paths"]) == operations(SPEC["paths"])


def test_every_response_matches_its_documented_schema(client):
    leagues = client.get("/api/leagues").json()
    for item in leagues:
        assert_matches_schema("League", item)

    for item in leagues:
        standings = client.get(f"/api/leagues/{item['id']}/standings").json()
        assert_matches_schema("Standings", standings)
        for row in standings["teams"]:
            assert_matches_schema("TeamDetail", client.get(f"/api/teams/{row['id']}").json())


def test_not_found_responses_match_the_error_schema(client):
    assert_matches_schema("Error", client.get("/api/leagues/nope/standings").json())
    assert_matches_schema("Error", client.get("/api/teams/nope").json())
