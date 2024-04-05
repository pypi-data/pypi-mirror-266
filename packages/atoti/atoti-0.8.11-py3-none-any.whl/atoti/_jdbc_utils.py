_JDBC_PREFIX = "jdbc:"


def normalize_jdbc_url(url: str, /) -> str:
    return url if url.startswith(_JDBC_PREFIX) else f"{_JDBC_PREFIX}{url}"
