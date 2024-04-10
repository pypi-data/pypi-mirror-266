from pathlib import Path


def cleanup() -> None:
    """Clean up frame files from the temporary directory and the CWD."""
    import tempfile

    for loc in [Path.cwd(), Path(tempfile.gettempdir())]:
        for f in loc.glob("xrframes_*.png"):
            f.unlink()
