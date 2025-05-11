import csv
import Levenshtein
import re


def get_relevant_authors(to_match: list[str], csv_path="authors.csv"):
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)
        all_info = [row[0] for row in reader if row]

    relevant = []

    for match in to_match:
        match_lower = match.lower()
        matches = [j for j in all_info if match_lower in j.lower()]

        if not matches:
            sorted_by_distance = sorted(
                all_info,
                key=lambda j: Levenshtein.distance(match_lower, j.lower())
            )
            matches = sorted_by_distance[:5]

        relevant.extend(matches)

    return list(set(relevant))


def clean_journal_name(journal: str) -> str:
    if not journal:
        return ""
    return re.split(r"[,\n]", journal)[0].strip().lower()


def get_relevant_journals(to_match: list[str], csv_path="journals.csv"):
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        next(reader)
        all_info = [row[0] for row in reader if row]

    relevant = []

    for match in to_match:
        match_lower = match.lower()
        matches = [j for j in all_info if match_lower in j.lower()]

        if not matches:
            sorted_by_distance = sorted(
                all_info,
                key=lambda j: Levenshtein.distance(match_lower, clean_journal_name(j))
            )
            matches = sorted_by_distance[:5]

        relevant.extend(matches)

    return list(set(relevant))