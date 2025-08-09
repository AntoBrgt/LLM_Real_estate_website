import re
from typing import Dict, Any

def extract_sections(text: str) -> Dict[str, str]:
    """
    Extract key HTML sections from the LLM-generated listing text.

    Args:
        text (str): The raw HTML string output by the language model.

    Returns:
        Dict[str, str]: A dictionary mapping section names to their full HTML content,
                        including the tags. Keys include:
                        'title', 'meta', 'h1', 'description',
                        'key-features', 'neighborhood', and 'cta'.
                        If a section is not found, its value is an empty string.
    """
    out = {}
    def find(pattern):
        m = re.search(pattern, text, flags=re.IGNORECASE)
        return m.group(0) if m else ''
    out['title'] = find(r'<title[^>]*>[\s\S]*?<\/title>')
    out['meta']  = find(r'<meta\s+name=["\']description["\'][^>]*>')
    out['h1']    = find(r'<h1[^>]*>[\s\S]*?<\/h1>')
    out['description'] = find(r'<section[^>]*id=["\']description["\'][^>]*>[\s\S]*?<\/section>')
    out['key-features'] = find(r'<ul[^>]*id=["\']key-features["\'][^>]*>[\s\S]*?<\/ul>')
    out['neighborhood'] = find(r'<section[^>]*id=["\']neighborhood["\'][^>]*>[\s\S]*?<\/section>')
    out['cta'] = find(r'<p[^>]*class=["\']call-to-action["\'][^>]*?[\s\S]*?<\/p>')
    return out

def strip_tags(s: str) -> str:
    """
    Remove all HTML tags from a string and trim surrounding whitespace.

    Args:
        s (str): Input string potentially containing HTML tags.

    Returns:
        str: Text content with all HTML tags removed.
    """
    return re.sub(r'<[^>]+>', '', s).strip()

def enforce_lengths_and_report(html: str) -> tuple[bool, str]:
    """
    Validate the structure and length constraints of the generated HTML listing.

    Checks that all required sections are present, and that:
    - Title length is <= 60 characters
    - Meta description length is <= 155 characters
    - Description paragraph length is between 500 and 700 characters inclusive
    - Number of <li> items in key features is between 3 and 5 inclusive

    Args:
        html (str): The complete generated HTML listing as a string.

    Returns:
        tuple[bool, str]: A tuple where the first element is True if all validations
                          pass, False otherwise. The second element is a message
                          describing success or the specific validation failure.
    """
    secs = extract_sections(html)
    missing = [k for k,v in secs.items() if not v]
    if missing:
        return False, f"Missing sections: {missing}"
    # title
    title_text = strip_tags(secs['title'])
    if len(title_text) > 60:
        return False, f"Title too long ({len(title_text)} > 60)"
    # meta
    meta_match = re.search(r'content\s*=\s*"(.*?)"', secs['meta'])
    if not meta_match:
        return False, "Meta tag missing content attribute"
    meta_text = meta_match.group(1)
    if len(meta_text) > 155:
        return False, f"Meta too long ({len(meta_text)} > 155)"
    # description paragraph
    pm = re.search(r'<section[^>]*id=["\']description["\'][^>]*>\s*<p>([\s\S]*?)<\/p>\s*<\/section>', secs['description'], flags=re.IGNORECASE)
    if not pm:
        return False, "Description paragraph not found"
    desc_text = pm.group(1).strip()
    if len(desc_text) < 500 or len(desc_text) > 700:
        return False, f"Description length {len(desc_text)} not in [500,700]"
    # key-features count
    li_count = len(re.findall(r'<li[^>]*>[\s\S]*?<\/li>', secs['key-features'], flags=re.IGNORECASE))
    if li_count < 3 or li_count > 5:
        return False, f"Key-features has {li_count} items (need 3-5)"
    return True, "OK"

def safe_get(data, keys, default=None):
    """
    Safely access nested dictionary keys returning a default if any key is missing or data is not a dict.

    Args:
        data (dict): The dictionary to traverse.
        keys (list[str]): List of nested keys to access in order.
        default: Value to return if any key is missing or data is invalid (default: None).

    Returns:
        The value at the nested key path if present, else the default value.
    """
    for key in keys:
        if not data or not isinstance(data, dict):
            return default
        data = data.get(key)
    return data if data is not None else default