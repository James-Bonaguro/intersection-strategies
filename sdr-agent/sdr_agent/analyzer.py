"""Website analysis module for scoring lead quality and classifying ownership."""

import re
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 10
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# ---------------------------------------------------------------------------
# Ownership classification patterns
# ---------------------------------------------------------------------------

# Footer / body patterns that signal the practice belongs to a larger group
_GROUP_PATTERNS = [
    r"a\s+proud\s+partner\s+of",
    r"proud\s+member\s+of",
    r"supported\s+by",
    r"managed\s+by",
    r"part\s+of\s+the\s+\w+\s+(family|network|group)",
    r"a\s+(portfolio|affiliated)\s+company",
    r"backed\s+by",
    r"an?\s+\w+\s+portfolio\s+company",
    r"\d{2,}\s+locations",
    r"\d{2,}\s+offices",
    r"nationwide\s+network",
    r"all\s+rights\s+reserved.*(?:management|partners|capital|holdings|group)",
    r"©.*(?:dental\s+care|management|partners|capital|holdings|group)\s+(?:llc|inc|corp)",
]

# Known DSO / group brands (dental-specific but expandable)
_KNOWN_GROUP_BRANDS = [
    "aspen dental",
    "heartland dental",
    "pacific dental",
    "dental care alliance",
    "smile brands",
    "dentalcorp",
    "mid-atlantic dental partners",
    "affordable care",
    "great expressions",
    "western dental",
    "birner dental",
    "interdent",
    "dental365",
    "mb2 dental",
    "north american dental group",
    "shore dental",
    "dental depot",
]

# Patterns suggesting independent ownership
_INDEPENDENT_PATTERNS = [
    r"family[\s-]owned",
    r"locally[\s-]owned",
    r"independently[\s-]owned",
    r"private\s+practice",
    r"sole\s+practitioner",
    r"owner[\s-]operated",
]

# ---------------------------------------------------------------------------
# Website quality scoring signals
# ---------------------------------------------------------------------------

_POSITIVE_SIGNALS = {
    "has_online_booking": (
        [r"book\s+(online|now|appointment)", r"schedule\s+(online|now|appointment)",
         r"request\s+appointment", r"online\s+scheduling"],
        15,
    ),
    "has_services_page": (
        [r"(our\s+)?services", r"treatments?\s+(we\s+offer|offered)"],
        10,
    ),
    "has_reviews_or_testimonials": (
        [r"testimonials?", r"patient\s+reviews", r"what\s+(our\s+)?(patients|clients)\s+say"],
        10,
    ),
    "has_team_page": (
        [r"(our|meet)\s+(the\s+)?(team|doctors?|staff|providers?)",
         r"about\s+(the\s+)?doctor"],
        5,
    ),
    "has_contact_form": (
        [r"contact\s+us", r"get\s+in\s+touch", r"send\s+(us\s+)?a?\s?message"],
        5,
    ),
    "has_insurance_info": (
        [r"(accepted\s+)?insurance", r"payment\s+options", r"financing"],
        5,
    ),
    "has_new_patient_info": (
        [r"new\s+patient", r"first\s+visit", r"welcome\s+new"],
        10,
    ),
    "has_blog": (
        [r"<a[^>]*href=[^>]*blog", r"/blog"],
        5,
    ),
}

_NEGATIVE_SIGNALS = {
    "has_broken_layout": (
        [r"lorem\s+ipsum", r"coming\s+soon", r"under\s+construction",
         r"site\s+not\s+found", r"page\s+not\s+found"],
        -20,
    ),
    "is_template_site": (
        [r"powered\s+by\s+wix", r"powered\s+by\s+squarespace",
         r"weebly\.com", r"wordpress\.com"],
        -5,
    ),
}


def analyze_website(url: str) -> dict:
    """
    Fetch a website and return quality score + ownership classification.

    Returns:
        Dict with keys:
            - website_score (int): 0-100 quality score
            - score_reasons (str): comma-separated reasons for the score
            - ownership_type (str): "Independent", "Group/DSO", or "Unknown"
            - ownership_signals (str): evidence found for classification
    """
    result = {
        "website_score": 0,
        "score_reasons": "",
        "ownership_type": "Unknown",
        "ownership_signals": "",
    }

    if not url:
        result["score_reasons"] = "No website"
        return result

    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(
            url,
            timeout=_REQUEST_TIMEOUT,
            headers={"User-Agent": _USER_AGENT},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.debug("Failed to fetch %s: %s", url, e)
        result["score_reasons"] = f"Unreachable ({type(e).__name__})"
        return result

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True).lower()
    html_lower = html.lower()

    # --- Quality scoring ---
    score = 30  # baseline: site exists and loads
    reasons = ["Site loads (+30)"]

    # Check SSL
    if resp.url.startswith("https://"):
        score += 5
        reasons.append("HTTPS (+5)")

    # Positive signals
    for signal_name, (patterns, points) in _POSITIVE_SIGNALS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE) or re.search(pat, html_lower, re.IGNORECASE):
                score += points
                label = signal_name.replace("has_", "").replace("_", " ").title()
                reasons.append(f"{label} (+{points})")
                break

    # Negative signals
    for signal_name, (patterns, points) in _NEGATIVE_SIGNALS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE) or re.search(pat, html_lower, re.IGNORECASE):
                score += points  # points are already negative
                label = signal_name.replace("has_", "").replace("is_", "").replace("_", " ").title()
                reasons.append(f"{label} ({points})")
                break

    result["website_score"] = max(0, min(100, score))
    result["score_reasons"] = "; ".join(reasons)

    # --- Ownership classification ---
    ownership, signals = _classify_ownership(text, html_lower, url)
    result["ownership_type"] = ownership
    result["ownership_signals"] = signals

    return result


def _classify_ownership(text: str, html_lower: str, url: str) -> tuple[str, str]:
    """Classify whether the business is independent or group-owned."""
    group_signals = []
    independent_signals = []

    # Check against known group brands
    for brand in _KNOWN_GROUP_BRANDS:
        if brand in text:
            group_signals.append(f"Known brand: {brand}")

    # Check group patterns
    for pat in _GROUP_PATTERNS:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            snippet = match.group(0)[:80]
            group_signals.append(f'Pattern: "{snippet}"')

    # Check footer specifically (often where affiliation is disclosed)
    footer_text = _extract_footer_text(html_lower)
    if footer_text:
        for pat in _GROUP_PATTERNS:
            match = re.search(pat, footer_text, re.IGNORECASE)
            if match:
                snippet = match.group(0)[:80]
                signal = f'Footer: "{snippet}"'
                if signal not in group_signals:
                    group_signals.append(signal)

    # Check for multi-location indicators in URL / text
    if re.search(r"locations?\s*(?:near|finder|search)", text):
        group_signals.append("Has location finder")
    if re.search(r"find\s+a\s+(location|office|clinic)", text):
        group_signals.append("Has location finder")

    # Check independent patterns
    for pat in _INDEPENDENT_PATTERNS:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            independent_signals.append(f'Pattern: "{match.group(0)[:60]}"')

    # Domain heuristic: generic/branded domains may signal group
    domain = urlparse(url).netloc.lower()
    domain_name = domain.replace("www.", "").split(".")[0]
    # Domains with numbers (e.g. dental365) or very generic names can signal groups
    if re.search(r"\d{3,}", domain_name):
        group_signals.append(f"Numeric domain: {domain}")

    # Decision logic
    if group_signals and not independent_signals:
        return "Group/DSO", "; ".join(group_signals)
    if independent_signals and not group_signals:
        return "Independent", "; ".join(independent_signals)
    if group_signals and independent_signals:
        # Group signals are typically more reliable
        return "Group/DSO", "; ".join(group_signals + ["(also found independent signals)"])

    return "Unknown", "No clear signals found"


def _extract_footer_text(html_lower: str) -> str:
    """Try to extract footer section text from HTML."""
    soup = BeautifulSoup(html_lower, "html.parser")
    footer = soup.find("footer")
    if footer:
        return footer.get_text(separator=" ", strip=True)
    # Fallback: look for a div with footer-like class/id
    for attr in ("id", "class"):
        el = soup.find(attrs={attr: re.compile(r"footer", re.IGNORECASE)})
        if el:
            return el.get_text(separator=" ", strip=True)
    return ""


def analyze_businesses(results: list[dict]) -> list[dict]:
    """
    Run website analysis on a list of business results.

    Adds website_score, score_reasons, ownership_type, and ownership_signals
    to each result dict in-place.
    """
    for i, r in enumerate(results):
        url = r.get("website", "")
        logger.info("Analyzing %d/%d: %s", i + 1, len(results), url or "(no website)")
        analysis = analyze_website(url)
        r.update(analysis)
    return results
