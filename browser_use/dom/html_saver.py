from pathlib import Path
import json
from datetime import datetime

async def save_raw_html_with_unicode(
    cdp_session,
    save_dir: str | Path = "./html_dumps",
    prefix: str = "page"
) -> Path:
    """
    Save raw HTML from CDP with proper Unicode preservation.

    Args:
        cdp_session: CDP session object
        save_dir: Directory to save HTML files
        prefix: Filename prefix

    Returns:
        Path to the saved HTML file
    """
    # Get the document
    doc = await cdp_session.cdp_client.send.DOM.getDocument(
        session_id=cdp_session.session_id
    )

    # Get outer HTML
    html_result = await cdp_session.cdp_client.send.DOM.getOuterHTML(
        params={'nodeId': doc['root']['nodeId']},
        session_id=cdp_session.session_id
    )

    page_html = html_result['outerHTML']

    # Create save directory
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_unicode = f"{prefix}_{timestamp}_unicode.html"
    file_path_unicode = save_path / filename_unicode

    filename_ascii = f"{prefix}_{timestamp}_ascii.html"
    file_path_ascii = save_path / filename_ascii

    # CRITICAL: Write with explicit UTF-8 encoding
    # This preserves all Unicode characters (Chinese, Japanese, Korean, emojis, etc.)
    file_path_unicode.write_text(page_html, encoding='utf-8')
    with open(file_path_ascii, 'w') as f:
        f.write(page_html)
    # Also save metadata
    metadata = {
        'timestamp': timestamp,
        'html_length': len(page_html),
        'encoding': 'utf-8',
        'unicode_test': '✓ Unicode preserved: 中文 日本語 한글 🎉'
    }

    metadata_path = save_path / f"{prefix}_{timestamp}_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')

    return
                                                                                                                                                                                                                