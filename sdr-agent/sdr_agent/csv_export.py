"""CSV export module for writing business search results to a local file."""

import csv
import os

HEADERS = [
    "Name",
    "Address",
    "Phone",
    "Website",
    "Rating",
    "Total Ratings",
    "Business Status",
    "Types",
    "Google Maps URL",
]


def export_to_csv(results: list[dict], output_path: str) -> str:
    """
    Write search results to a CSV file.

    Args:
        results: List of business result dicts.
        output_path: File path for the output CSV.

    Returns:
        Absolute path to the written CSV file.
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        for r in results:
            writer.writerow(_result_to_row(r))

    return os.path.abspath(output_path)


def _result_to_row(result: dict) -> list[str]:
    """Convert a result dict to a row of cell values."""
    return [
        str(result.get("name", "")),
        str(result.get("address", "")),
        str(result.get("phone", "")),
        str(result.get("website", "")),
        str(result.get("rating", "")),
        str(result.get("total_ratings", "")),
        str(result.get("business_status", "")),
        str(result.get("types", "")),
        str(result.get("google_maps_url", "")),
    ]
