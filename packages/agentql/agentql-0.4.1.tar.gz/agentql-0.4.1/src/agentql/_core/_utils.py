def ensure_url_scheme(url: str) -> str:
    """
    Ensure that the URL has a scheme.
    """
    if not url.startswith(("http://", "https://", "file://")):
        return "https://" + url
    return url
