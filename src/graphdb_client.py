"""Query character relationships from the Game of Thrones GraphDB."""

from __future__ import annotations

import os
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GRAPHDB_URL = os.getenv("GRAPHDB_URL", "http://localhost:7200").rstrip("/")
GRAPHDB_REPOSITORY = os.getenv("GRAPHDB_REPOSITORY", "BIP-LLM")
NAMESPACE = "http://gameofthrones.org#"
RELATIONSHIPS_GRAPH = "http://gameofthrones.org#relationships"
REQUEST_TIMEOUT = (5, 30)


class GraphDBQueryError(RuntimeError):
    """Raised when a GraphDB query cannot be completed or decoded."""


def execute_query(query: str) -> list[dict]:
    """Execute a SPARQL SELECT query and return its result bindings."""
    repository = quote(GRAPHDB_REPOSITORY, safe="")
    endpoint = f"{GRAPHDB_URL}/repositories/{repository}"

    try:
        response = requests.post(
            endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise GraphDBQueryError(f"GraphDB query timed out at {endpoint}.") from exc
    except requests.ConnectionError as exc:
        raise GraphDBQueryError(f"Could not connect to GraphDB at {endpoint}.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise GraphDBQueryError(
            f"GraphDB returned HTTP {status} for repository "
            f"'{GRAPHDB_REPOSITORY}'."
        ) from exc
    except requests.RequestException as exc:
        raise GraphDBQueryError(f"GraphDB request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise GraphDBQueryError("GraphDB returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise GraphDBQueryError("GraphDB returned a malformed SPARQL response.")

    results = payload.get("results")
    if not isinstance(results, dict):
        raise GraphDBQueryError("GraphDB response is missing a valid 'results' object.")

    bindings = results.get("bindings")
    if not isinstance(bindings, list) or not all(
        isinstance(binding, dict) for binding in bindings
    ):
        raise GraphDBQueryError(
            "GraphDB response is missing valid SPARQL result bindings."
        )

    return bindings


def normalize_character_name(name: str) -> str:
    """Convert a name containing spaces or underscores to an RDF local name."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Character name must be a non-empty string.")

    words = re.split(r"[\s_]+", name.strip())
    normalized_words: list[str] = []
    for word in words:
        if re.fullmatch(r"[ivxlcdm]+", word, flags=re.IGNORECASE):
            normalized_words.append(word.upper())
        else:
            normalized_words.append(word[:1].upper() + word[1:].lower())

    return "_".join(normalized_words)


def uri_to_readable_name(uri: str) -> str:
    """Convert an RDF URI fragment or final path component to readable text."""
    if not isinstance(uri, str) or not uri:
        return ""

    parsed = urlsplit(uri)
    local_name = parsed.fragment or parsed.path.rsplit("/", 1)[-1]
    readable = unquote(local_name).replace("_", " ")
    readable = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", readable)
    return re.sub(r"\s+", " ", readable).strip()


def predicate_to_readable(predicate: str) -> str:
    """Convert a camelCase predicate name to lowercase readable text."""
    readable = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", predicate)
    readable = readable.replace("_", " ")
    return re.sub(r"\s+", " ", readable).strip().lower()


def get_character_relations(character_name: str) -> list[dict[str, str]]:
    """Return all outgoing and incoming relationships for a character."""
    local_name = normalize_character_name(character_name)
    character_uri = f"{NAMESPACE}{quote(local_name, safe='-._~')}"

    query = f"""
SELECT ?source ?relation ?target ?direction
WHERE {{
  GRAPH <{RELATIONSHIPS_GRAPH}> {{
    {{
      <{character_uri}> ?relation ?target .
      BIND(<{character_uri}> AS ?source)
      BIND("outgoing" AS ?direction)
    }}
    UNION
    {{
      ?source ?relation <{character_uri}> .
      BIND(<{character_uri}> AS ?target)
      BIND("incoming" AS ?direction)
    }}
    FILTER(isIRI(?source) && isIRI(?target))
  }}
}}
ORDER BY ?direction ?relation ?source ?target
""".strip()

    relations: list[dict[str, str]] = []
    for binding in execute_query(query):
        try:
            source_uri = binding["source"]["value"]
            relation_uri = binding["relation"]["value"]
            target_uri = binding["target"]["value"]
            direction = binding["direction"]["value"]
        except (KeyError, TypeError) as exc:
            raise GraphDBQueryError(
                "GraphDB returned an incomplete relationship binding."
            ) from exc

        if not all(
            isinstance(value, str)
            for value in (source_uri, relation_uri, target_uri, direction)
        ) or direction not in {"outgoing", "incoming"}:
            raise GraphDBQueryError(
                "GraphDB returned a malformed relationship binding."
            )

        parsed_relation = urlsplit(relation_uri)
        relation = parsed_relation.fragment or parsed_relation.path.rsplit("/", 1)[-1]
        relation = unquote(relation)

        relations.append(
            {
                "source": uri_to_readable_name(source_uri),
                "relation": relation,
                "target": uri_to_readable_name(target_uri),
                "direction": direction,
            }
        )

    return relations


def get_kg_context(character_name: str) -> str:
    """Render all character relationships as complete readable sentences."""
    readable_character = uri_to_readable_name(
        f"{NAMESPACE}{normalize_character_name(character_name)}"
    )
    relations = get_character_relations(character_name)

    if not relations:
        return f"No relationships found for {readable_character}."

    return "\n".join(
        f"{relation['source']} "
        f"{predicate_to_readable(relation['relation'])} "
        f"{relation['target']}."
        for relation in relations
    )


def main() -> None:
    """Prompt for a character and print readable GraphDB relationships."""
    try:
        character_name = input("Character name: ").strip()
        readable_character = uri_to_readable_name(
            f"{NAMESPACE}{normalize_character_name(character_name)}"
        )
        context = get_kg_context(character_name)
    except (ValueError, GraphDBQueryError) as exc:
        print(f"Error: {exc}")
        return

    print(f"Relationships for {readable_character}:")
    print(context)


if __name__ == "__main__":
    main()
