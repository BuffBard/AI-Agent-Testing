from fnmatch import fnmatch
from pathlib import Path

SAFE_ROOT = Path(__file__).resolve().parent

SENSITIVE_PATTERNS = [".env", ".env.*"]


def _is_allowed(resolved: Path) -> bool:
    """Whether a resolved path is inside SAFE_ROOT and not sensitive."""
    if not resolved.is_relative_to(SAFE_ROOT):
        return False
    return not any(
        fnmatch(part, pattern)
        for part in resolved.relative_to(SAFE_ROOT).parts
        for pattern in SENSITIVE_PATTERNS
    )


def _resolve_safe(path: str) -> Path:
    """Whether a resolved path allowed through permissions."""
    target = (SAFE_ROOT / path).resolve()

    if not _is_allowed(target):
        raise PermissionError("Access denied or file not found.")

    return target


def read_safe_file(path: str) -> str:
    """Read a UTF-8 text file from the project directory.

    Args:
        path: File path relative to the project root, e.g. "docs/readme.txt".
    """
    target = _resolve_safe(path)
    if not target.is_file():
        raise PermissionError("Access denied or file not found.")

    return target.read_text(encoding="utf-8")

def write_safe_file(path: str, content: str) -> str:
    """Write a UTF-8 text file from the project directory.

    Args:
        path: File path relative to the project root, e.g. "docs/readme.txt"
        content: what to write to file.
    """
    target = _resolve_safe(path)
    if not target.is_file():
        raise PermissionError("Access denied or file not found.")

    return target.write_text(content, encoding="utf-8")


def list_directory(path: str = ".") -> str:
    """List the contents of a directory in the project. Subdirectories end with "/".

    Args:
        path: Directory path relative to the project root. Defaults to the root.
    """
    target = _resolve_safe(path)
    if not target.is_dir():
        raise PermissionError("Access denied or directory not found.")

    entries = sorted(
        entry.name + "/" if entry.is_dir() else entry.name
        for entry in target.iterdir()
        if _is_allowed(entry.resolve())
    )
    return "\n".join(entries) or "(empty directory)"