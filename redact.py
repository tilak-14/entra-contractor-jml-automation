"""
redact.py — Strips real tenant/user identifiers from Lifecycle Workflow JSON exports
before they are committed to a public GitHub repo.

Usage:
    python redact.py input_raw.json output_redacted.json

What it does:
    - Replaces any GUID-looking id with a zero-padded placeholder GUID (keeps structure valid)
    - Replaces any string containing "onmicrosoft.com" or an email pattern with a placeholder
    - Leaves task definition IDs (public Microsoft constants) untouched, since those are
      documented Microsoft task identifiers, not tenant-specific secrets.
"""

import json
import re
import sys

GUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Known public Microsoft task definition IDs -- safe to keep, NOT tenant secrets
KNOWN_TASK_IDS = {
    "70b29d51-b59a-4773-9280-8841dfd3f2ea",
    "3C860712-2D37-42A4-928F-5C93935D26A1".lower(),
    "1b555e50-7f65-41d5-b514-5894a026d10d",
    "aab41899-9972-422a-9d97-f626014578b7",
    "c1ec1e76-f374-4375-aaa6-0bb6bd4c60be",
    "683c87a4-2ad4-420b-97d4-220d90afcd24",
    "22085229-5809-45e8-97fd-270d28d66910",
    "e440ed8d-25a1-4618-84ce-091ed5be5594",
    "6fc52c9d-398b-4305-9763-15f42c1676fc",
    "4262b724-8dba-4fad-afc3-43fcbb497a0e",
    "1dfdfcc7-52fa-4c2e-bf3a-e3919cc12950",
    "1953a66c-751c-45e5-8bfe-01462c70da3c",
    "b3a31406-2a15-4c9a-b25b-a658fa5f07fc",
    "06aa7acb-01af-4824-8899-b14e5ed788d6",
    "81f7b200-2816-4b3b-8c5d-dc556f07b024",
    "4a0b64f2-c7ec-46ba-b117-18f262946c50",
    "42ae2956-193d-4f39-be06-691b8ac4fa1d",
    "498770d9-bab7-4e4c-b73d-5ded82a1d0b3",
    "5fc402a8-daaf-4b7b-9203-da868b05fc5f",
    "509589a4-0466-4471-829e-49c5e502bdee",
}

counter = {"n": 0}


def guid_replacer(match):
    val = match.group(0).lower()
    if val in KNOWN_TASK_IDS:
        return match.group(0)  # keep public task definition IDs as-is
    counter["n"] += 1
    return f"00000000-0000-0000-0000-{counter['n']:012d}"


def redact_text(text: str) -> str:
    text = GUID_PATTERN.sub(guid_replacer, text)
    text = EMAIL_PATTERN.sub("user@example.com", text)
    text = text.replace("28q148.onmicrosoft.com", "contoso.onmicrosoft.com")
    return text


def main():
    if len(sys.argv) != 3:
        print("Usage: python redact.py input_raw.json output_redacted.json")
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    redacted_text = redact_text(raw_text)

    # Validate it's still valid JSON after redaction
    parsed = json.loads(redacted_text)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2)

    print(f"Redacted {counter['n']} tenant-specific identifier(s).")
    print(f"Output written to {output_path}")
    print("Review the file manually before committing -- this script catches GUIDs and emails,")
    print("but double-check display names, notes, or free-text fields for anything identifying.")


if __name__ == "__main__":
    main()
