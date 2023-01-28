import warnings


def rst_to_html(rst: str, unescape: bool = True) -> str:
    """Convert rST string into HTML."""
    from docutils.examples import html_body

    try:
        body: bytes = html_body(
            rst, input_encoding="utf-8", output_encoding="utf-8"
        )
        html = body.decode(encoding="utf-8")
        if unescape:
            from xml.sax.saxutils import unescape as _unescape

            html = _unescape(html)

    except Exception as e:
        warnings.warn(
            "Could not convert string into HTML due to "
            f"{type(e).__name__}: {e}",
            UserWarning,
        )
        html = rst
    return html
