"""Github and data handler module."""

import re
from typing import Any, Dict, List

import requests


RAW_PUBLIC_APIS_URL = (
    "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"
)
ROW_REGEX = re.compile(
    r"\| +?(.+?) +?\| +?(.+?) +?\| +?(.+?) +?\| +?(.+?) +?\| +?(.+?) +?\|"
)
MARKDOWN_LINK_REGEX = re.compile(r"\[(.+?)\]\((.+?)\)")
MARKDOWN_LINK_EXCLUDE_REGEX = re.compile(r"\[.+?\]\(^#.+?\)")
REQUEST_TIMEOUT = 10


def yes_no_to_bool(value: str) -> bool:
    """Convert yes/no to bool.

    Args:
        value (str): Value to convert.

    Returns:
        bool: Converted value.
    """
    return value.strip().lower() == "yes"


def is_yes_no(value: Any) -> bool:
    """Determine if value is yes/no.

    Args:
        value (Any): Value to check.

    Returns:
        bool: Value is yes/no.
    """
    if isinstance(value, str) is False:
        return False

    lowered = value.lower().strip()

    return bool(lowered == "yes" or lowered == "no")


def get_raw_public_apis() -> str:
    """Get raw public APIs from Github.

    Returns:
        str: Raw public APIs from Github.
    """
    resp = requests.get(RAW_PUBLIC_APIS_URL, timeout=REQUEST_TIMEOUT)
    text = resp.text
    return text


def parse_rows(raw_text: str) -> List[Dict[str, Any]]:
    """Parse rows from raw text.

    Args:
        raw_text (str): Raw text to parse.

    Returns:
        List[Dict[str, Any]]: List of parsed rows.
    """
    # Iterate over all of the headers for each of the sections
    # and then get all lines that are within a table under that
    # header that contain a link.
    apis = []

    category = None
    for line in raw_text.split("\n"):
        line = line.strip()

        # If we encounter a new category, update the category
        if line.startswith("### "):
            category = line.replace("### ", "").strip()

        # If we encounter a line that starts and ends with a pipe
        if (
            category is not None
            and ROW_REGEX.search(line) is not None
            and MARKDOWN_LINK_REGEX.search(line) is not None
            and MARKDOWN_LINK_EXCLUDE_REGEX.search(line) is None
        ):
            # Split the line by pipes
            parts = ROW_REGEX.findall(line)[0]
            # Get the link and description
            md_link, description = parts[0:2]
            # Get the name and link from the markdown link
            name, link = re.findall(MARKDOWN_LINK_REGEX, md_link)[0]
            # Determine auth method
            auth_method = parts[2].strip().lower().replace("`", "")
            if "oauth" in auth_method:
                auth_method = "oauth"
            elif "apikey" in auth_method or "api key" in auth_method:
                auth_method = "apikey"
            elif is_yes_no(auth_method):
                auth_method = yes_no_to_bool(auth_method)
            else:
                auth_method = auth_method.strip().lower()

            # Determine if HTTPS is supported
            https = yes_no_to_bool(parts[3].strip().lower())
            # Determine if CORS is supported
            cors = yes_no_to_bool(parts[4].strip().lower())

            # Add the API to the list of APIs
            apis.append(
                {
                    "name": name,
                    "description": description,
                    "auth_method": auth_method,
                    "https": https,
                    "cors": cors,
                    "link": link,
                    "category": category,
                }
            )

    return apis
