import typing as t

SIZE_UNIT: t.Final = "B"
DEFAULT_PRECISION: t.Final = 2


def size(size_bytes: int | float, precision: int = DEFAULT_PRECISION) -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.{precision}f} {unit}{SIZE_UNIT}"
        size_bytes /= 1024.0
    return f"{size_bytes:.{precision}f} Yi{SIZE_UNIT}"
