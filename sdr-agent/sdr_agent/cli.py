"""CLI entry point for the SDR Agent business search tool."""

import argparse
import os
import sys

import googlemaps

from .search import enrich_results, search_businesses
from .sheets import export_to_sheet, get_sheets_client


def main():
    parser = argparse.ArgumentParser(
        description="SDR Agent — Search for businesses and export leads to Google Sheets."
    )
    parser.add_argument(
        "query",
        help="Search query (e.g. 'dental offices', 'plumbers', 'SaaS companies')",
    )
    parser.add_argument(
        "--location",
        required=True,
        help="Location to search around (e.g. 'Austin, TX', 'San Francisco, CA')",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=50000,
        help="Search radius in meters (default: 50000, max: 50000)",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=60,
        help="Maximum number of results (default: 60, max: 60)",
    )
    parser.add_argument(
        "--sheet-id",
        required=True,
        help="Google Spreadsheet ID to export results to",
    )
    parser.add_argument(
        "--worksheet",
        default="Sheet1",
        help="Worksheet tab name (default: Sheet1)",
    )
    parser.add_argument(
        "--google-api-key",
        default=os.environ.get("GOOGLE_MAPS_API_KEY"),
        help="Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)",
    )
    parser.add_argument(
        "--credentials-file",
        default=os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "credentials.json"),
        help="Path to Google service account JSON file (default: credentials.json)",
    )
    parser.add_argument(
        "--no-enrich",
        action="store_true",
        help="Skip fetching detailed info (phone, website) for each result",
    )

    args = parser.parse_args()

    if not args.google_api_key:
        print("Error: Google Maps API key is required.")
        print("Set GOOGLE_MAPS_API_KEY env var or pass --google-api-key.")
        sys.exit(1)

    if not os.path.exists(args.credentials_file):
        print(f"Error: Credentials file not found: {args.credentials_file}")
        print("Set GOOGLE_SERVICE_ACCOUNT_FILE env var or pass --credentials-file.")
        sys.exit(1)

    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=args.google_api_key)

    # Search for businesses
    print(f"Searching for '{args.query}' near {args.location}...")
    results = search_businesses(
        client=gmaps,
        query=args.query,
        location=args.location,
        radius=args.radius,
        max_results=args.max_results,
    )
    print(f"Found {len(results)} results.")

    if not results:
        print("No results found. Try broadening your search.")
        sys.exit(0)

    # Enrich with details (phone, website)
    if not args.no_enrich:
        print("Fetching detailed info for each business...")
        results = enrich_results(gmaps, results)

    # Export to Google Sheets
    print(f"Exporting to Google Sheet...")
    sheets_client = get_sheets_client(args.credentials_file)
    url = export_to_sheet(
        client=sheets_client,
        spreadsheet_id=args.sheet_id,
        results=results,
        worksheet_name=args.worksheet,
    )
    print(f"Done! Results exported to: {url}")


if __name__ == "__main__":
    main()
