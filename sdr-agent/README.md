# SDR Agent — Business Search CLI

Search for businesses using Google Maps Places API and export leads to Google Sheets.

## Setup

### 1. Install dependencies

```bash
cd sdr-agent
pip install -r requirements.txt
```

### 2. Google Maps API key

Get an API key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) with the **Places API** enabled.

```bash
export GOOGLE_MAPS_API_KEY=your-key-here
```

### 3. Google Sheets service account

1. Create a service account in [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Download the JSON credentials file and save it as `credentials.json` in this directory
3. Share your target Google Sheet with the service account email (give it **Editor** access)

## Usage

```bash
python -m sdr_agent "dental offices" \
  --location "Austin, TX" \
  --sheet-id "your-google-spreadsheet-id"
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `query` | Search query (e.g. "plumbers", "SaaS companies") | *required* |
| `--location` | Location to search around | *required* |
| `--sheet-id` | Google Spreadsheet ID to export to | *required* |
| `--radius` | Search radius in meters | 50000 |
| `--max-results` | Max results to return | 60 |
| `--worksheet` | Worksheet tab name | Sheet1 |
| `--no-enrich` | Skip fetching phone/website details | false |
| `--google-api-key` | Google Maps API key | `$GOOGLE_MAPS_API_KEY` |
| `--credentials-file` | Service account JSON path | credentials.json |

### Examples

Search for restaurants in San Francisco:
```bash
python -m sdr_agent "restaurants" --location "San Francisco, CA" --sheet-id "1abc..."
```

Quick search without phone/website enrichment:
```bash
python -m sdr_agent "law firms" --location "New York, NY" --sheet-id "1abc..." --no-enrich
```

Search within a smaller radius (5km):
```bash
python -m sdr_agent "gyms" --location "Chicago, IL" --radius 5000 --sheet-id "1abc..."
```

## Output

Results are written to Google Sheets with the following columns:

- Name
- Address
- Phone
- Website
- Rating
- Total Ratings
- Business Status
- Types
- Google Maps URL
