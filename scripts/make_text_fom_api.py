import argparse
import json
from pathlib import Path


def list_to_english(items: list[str]) -> str:
	if not items:
		return ""
	if len(items) == 1:
		return items[0]
	if len(items) == 2:
		return f"{items[0]} and {items[1]}"
	return f"{', '.join(items[:-1])} and {items[-1]}"


def extract_raw_id(url: str) -> str:
	if not url:
		return "unknown"
	return url.rstrip("/").split("/")[-1]


def extract_numeric_id(url: str) -> str:
	return f"CHAR-{extract_raw_id(url).zfill(3)}"


def extract_book_ids(book_urls: list[str]) -> list[str]:
	return [extract_raw_id(url) for url in book_urls if url]


def extract_resource_ids(urls: list[str]) -> list[str]:
	return [extract_raw_id(url) for url in urls if url]


def get_display_name(character: dict) -> str:
	name = (character.get("name") or "").strip()
	aliases = [a.strip() for a in character.get("aliases", []) if a and a.strip()]

	if name:
		return name
	if aliases:
		return aliases[0]
	return "Unknown character"


def build_intro_sentence(character: dict, display_name: str) -> str:
	aliases = [a.strip() for a in character.get("aliases", []) if a and a.strip()]
	gender = (character.get("gender") or "Unknown").strip().lower()

	if gender in {"", "unknown", "n/a"}:
		gender_phrase = "a character"
	else:
		gender_phrase = f"a {gender} character"

	if character.get("name", "").strip() and aliases:
		return f"{display_name}, commonly known as {aliases[0]}, is {gender_phrase}."

	return f"{display_name} is {gender_phrase}."


def build_aliases_sentence(character: dict, display_name: str) -> str | None:
	aliases = [a.strip() for a in character.get("aliases", []) if a and a.strip()]
	if not aliases:
		return None

	if character.get("name", "").strip() and aliases:
		remaining_aliases = aliases[1:]
		if remaining_aliases:
			return f"Other known aliases for {display_name} include {list_to_english(remaining_aliases)}."
		return None

	if len(aliases) > 1:
		return f"{display_name} is also known as {list_to_english(aliases[1:])}."

	return None


def build_culture_sentence(character: dict, pronoun: str) -> str | None:
	culture = (character.get("culture") or "").strip()
	if not culture:
		return None
	return f"{pronoun} is from {culture} culture."


def build_birth_sentence(character: dict, pronoun: str) -> str | None:
	born = (character.get("born") or "").strip()
	if not born:
		return None
	return f"{pronoun} was born {born}."


def build_death_sentence(character: dict, pronoun: str) -> str | None:
	died = (character.get("died") or "").strip()
	if not died:
		return None
	return f"{pronoun} died {died}."


def build_titles_sentence(character: dict, pronoun: str) -> str | None:
	titles = [t.strip() for t in character.get("titles", []) if t and t.strip()]
	if not titles:
		return None
	if len(titles) == 1:
		return f"{pronoun} holds the title {titles[0]}."
	return f"{pronoun} holds the titles {list_to_english(titles)}."


def build_tv_sentence(character: dict, pronoun: str) -> str | None:
	seasons = [s.strip() for s in character.get("tvSeries", []) if s and s.strip()]
	if not seasons:
		return None

	season_numbers = []
	for season in seasons:
		if season.lower().startswith("season "):
			season_numbers.append(season.split(" ", 1)[1])
		else:
			season_numbers = []
			break

	if season_numbers:
		seasons_text = f"Seasons {list_to_english(season_numbers)}"
	else:
		seasons_text = list_to_english(seasons)

	return f"{pronoun} appears in {seasons_text} of the television series."


def build_actor_sentence(character: dict) -> str | None:
	actors = [a.strip() for a in character.get("playedBy", []) if a and a.strip()]
	if not actors:
		return None
	return f"The character is played by {list_to_english(actors)}."


def build_books_sentence(character: dict, pronoun: str) -> str | None:
	books = extract_book_ids(character.get("books", []))
	if not books:
		return None
	label = "book" if len(books) == 1 else "books"
	return f"{pronoun} appears in {label} {list_to_english(books)}."


def build_pov_books_sentence(character: dict, pronoun: str) -> str | None:
	pov_books = extract_resource_ids(character.get("povBooks", []))
	if not pov_books:
		return None
	label = "book" if len(pov_books) == 1 else "books"
	return f"{pronoun} has point-of-view chapters in {label} {list_to_english(pov_books)}."


def get_pronoun(character: dict) -> str:
	gender = (character.get("gender") or "").strip().lower()
	if gender == "female":
		return "She"
	if gender == "male":
		return "He"
	return "They"


def character_to_text_record(character: dict) -> dict:
	char_id = extract_numeric_id(character.get("url", ""))
	display_name = get_display_name(character)
	pronoun = get_pronoun(character)

	sentences = [build_intro_sentence(character, display_name)]

	aliases_sentence = build_aliases_sentence(character, display_name)
	if aliases_sentence:
		sentences.append(aliases_sentence)

	culture_sentence = build_culture_sentence(character, pronoun)
	if culture_sentence:
		sentences.append(culture_sentence)

	birth_sentence = build_birth_sentence(character, pronoun)
	if birth_sentence:
		sentences.append(birth_sentence)

	death_sentence = build_death_sentence(character, pronoun)
	if death_sentence:
		sentences.append(death_sentence)

	titles_sentence = build_titles_sentence(character, pronoun)
	if titles_sentence:
		sentences.append(titles_sentence)

	tv_sentence = build_tv_sentence(character, pronoun)
	if tv_sentence:
		sentences.append(tv_sentence)

	actor_sentence = build_actor_sentence(character)
	if actor_sentence:
		sentences.append(actor_sentence)

	books_sentence = build_books_sentence(character, pronoun)
	if books_sentence:
		sentences.append(books_sentence)

	pov_books_sentence = build_pov_books_sentence(character, pronoun)
	if pov_books_sentence:
		sentences.append(pov_books_sentence)

	return {
		"id": char_id,
		"text": "\n".join(sentences),
	}


def transform_characters(input_path: Path, output_path: Path) -> None:
	with input_path.open("r", encoding="utf-8") as f:
		characters = json.load(f)

	transformed = [character_to_text_record(character) for character in characters]

	with output_path.open("w", encoding="utf-8") as f:
		json.dump(transformed, f, ensure_ascii=False, indent=2)


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Convert GOT character JSON into text records with ids."
	)
	parser.add_argument(
		"-i",
		"--input",
		default="characters.json",
		help="Path to input characters JSON file",
	)
	parser.add_argument(
		"-o",
		"--output",
		default="characters_text.json",
		help="Path to output JSON file",
	)

	args = parser.parse_args()
	transform_characters(Path(args.input), Path(args.output))


if __name__ == "__main__":
	main()
