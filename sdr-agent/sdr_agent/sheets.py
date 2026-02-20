"""Google Sheets export module for writing business search results."""

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

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


def get_sheets_client(credentials_path: str) -> gspread.Client:
    """Authenticate and return a gspread client using a service account."""
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return gspread.authorize(creds)


def export_to_sheet(
    client: gspread.Client,
    spreadsheet_id: str,
    results: list[dict],
    worksheet_name: str = "Sheet1",
) -> str:
    """
    Write search results to a Google Sheet.

    Args:
        client: Authenticated gspread client.
        spreadsheet_id: ID of the target Google Spreadsheet.
        results: List of business result dicts.
        worksheet_name: Name of the worksheet tab to write to.

    Returns:
        URL of the updated spreadsheet.
    """
    spreadsheet = client.open_by_key(spreadsheet_id)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name, rows=len(results) + 1, cols=len(HEADERS)
        )

    rows = [_result_to_row(r) for r in results]
    data = [HEADERS] + rows

    worksheet.clear()
    worksheet.update(range_name="A1", values=data)

    return spreadsheet.url


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
