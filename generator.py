import time
from typing import Dict, Any

from llm_client import invoke_llm
from prompt import build_prompt
from validation import enforce_lengths_and_report

def generate_with_validation(data: Dict[str, Any], tone: str = "friendly", retries: int = 2) -> str:
    """
    Generate an HTML real estate listing using a language model, validating output length and format.

    This function constructs a prompt from input data and tone, then calls the LLM multiple times
    (up to retries+1 attempts) to obtain valid HTML output. It validates the output for required
    HTML structure and length constraints. If validation fails after all retries, it returns
    the last output received (even if invalid) or raises an error if no output was generated.

    Args:
        data (Dict[str, Any]): Input JSON-like dictionary with listing data.
        tone (str): Style tone for the listing (e.g., "friendly", "formal").
        retries (int): Number of retries allowed for generating valid output.

    Returns:
        str: Generated HTML listing as a string.

    Raises:
        RuntimeError: If no valid output is generated and no last output is available.
    """
    language = data.get('language','en')
    prompt = build_prompt(data, language, tone)
    last_error = None
    last_result = None
    for attempt in range(1, retries + 2):
        start = time.time()
        try:
            result = invoke_llm(prompt)
            last_result = result
        except Exception as e:
            result = ""
            last_error = f"LLM error: {e}"
        elapsed = time.time() - start
        ok, msg = (False, "No output") if not result else enforce_lengths_and_report(result)
        print(f"[attempt {attempt}] valid={ok} ({msg}) — {elapsed:.2f}s")
        if ok:
            return result
        last_error = msg
        prompt += "\n\nIMPORTANT: Regenerate with exact tags, exact order, and strict length limits (title<=60, meta<=155, description 500-700)."
        time.sleep(0.4)
    if last_result is not None:
        print(f"Warning: Returning last LLM output despite validation failure: {last_error}")
        return last_result
    raise RuntimeError(f"Failed to generate valid output after {retries+1} attempts. Last error: {last_error}")

def generate_listing(data, tone="friendly", retries=2):
    """
    Wrapper function to generate a real estate listing with a given tone and retry count.

    Args:
        data (dict): Input data dictionary for the listing.
        tone (str): Tone/style for generation, default is "friendly".
        retries (int): Number of retries for validation attempts, default is 2.

    Returns:
        str: Generated HTML listing as string.
    """
    return generate_with_validation(data, tone=tone, retries=retries)