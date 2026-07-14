from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests


API_URL = "https://www.anapioficeandfire.com/api/characters"
MAX_PAGE_SIZE = 50


def fetch_all_characters(page_size: int = MAX_PAGE_SIZE) -> list[dict[str, Any]]:
	if page_size < 1 or page_size > MAX_PAGE_SIZE:
		raise ValueError(f"page_size must be between 1 and {MAX_PAGE_SIZE}")

	characters: list[dict[str, Any]] = []
	page = 1

	while True:
		response = requests.get(
			API_URL,
			params={"page": page, "pageSize": page_size},
			timeout=30,
		)
		response.raise_for_status()

		page_items = response.json()
		if not isinstance(page_items, list):
			raise ValueError("Unexpected response format: expected a list of characters")

		characters.extend(page_items)

		link_header = response.headers.get("Link", "")
		if 'rel="next"' not in link_header:
			break

		page += 1

	return characters


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Fetch every character from An API of Ice and Fire."
	)
	parser.add_argument(
		"--output",
		type=Path,
		help="Optional path to save the collected characters as JSON.",
	)
	parser.add_argument(
		"--page-size",
		type=int,
		default=MAX_PAGE_SIZE,
		help=f"Number of characters to request per page (1-{MAX_PAGE_SIZE}).",
	)
	args = parser.parse_args()

	characters = fetch_all_characters(page_size=args.page_size)
	print(f"Fetched {len(characters)} characters from the API.")

	if args.output:
		args.output.write_text(json.dumps(characters, indent=2, ensure_ascii=False), encoding="utf-8")
		print(f"Saved to {args.output}")
	else:
		print(json.dumps(characters[:3], indent=2, ensure_ascii=False))
		if len(characters) > 3:
			print("...")


if __name__ == "__main__":
	main()
