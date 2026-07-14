import json
import re
import unicodedata

from rdflib import Dataset, Namespace, URIRef


INPUT_FILE = "characters.json"
OUTPUT_FILE = "got_relationships.trig"

GOT = Namespace("http://gameofthrones.org#")
GRAPH = URIRef("http://gameofthrones.org#relationships")


RELATION_MAPPING = {
    "parents": GOT.childOf,
    "parentOf": GOT.parentOf,
    "siblings": GOT.siblingOf,
    "killed": GOT.killed,
    "killedBy": GOT.killedBy,
    "marriedEngaged": GOT.marriedOrEngagedTo,
    "serves": GOT.serves,
    "servedBy": GOT.servedBy,
    "guardedBy": GOT.guardedBy,
    "guardianOf": GOT.guardianOf,
}


def load_characters():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)["characters"]


def sanitize(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode()

    name = re.sub(r"[^A-Za-z0-9]", "_", name)
    name = re.sub(r"_+", "_", name)

    return name.strip("_")


def character_uri(name: str):
    return GOT[sanitize(name)]


def main():

    characters = load_characters()

    dataset = Dataset()

    dataset.bind("", GOT)

    graph = dataset.graph(GRAPH)

    triple_count = 0

    for character in characters:

        if "characterName" not in character:
            continue

        source = character_uri(character["characterName"])

        for json_relation, rdf_relation in RELATION_MAPPING.items():

            if json_relation not in character:
                continue

            for target_name in character[json_relation]:

                target = character_uri(target_name)

                graph.add(
                    (
                        source,
                        rdf_relation,
                        target,
                    )
                )

                triple_count += 1

    dataset.serialize(
        OUTPUT_FILE,
        format="trig",
    )

    print(f"Created {OUTPUT_FILE}")
    print(f"Relationships: {triple_count}")


if __name__ == "__main__":
    main()