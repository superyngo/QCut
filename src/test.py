from app.utils import logger
from datetime import datetime
from pathlib import Path
import re


def _convert_datestamp_to_epoch(datestamp: str) -> int | None:
    """Convert a datestamp in the format YYYYMMDDHHMMSS to epoch time."""
    try:
        dt = datetime.strptime(datestamp, "%Y%m%d%H%M%S")
        return int(dt.timestamp())
    except ValueError as e:
        logger.error(f"Failed to convert datestamp {datestamp} to epoch: {str(e)}")
        return None


def _extract_first_datestamp_epoch(filename: Path | str) -> int | None:
    """Extract the epoch time from the first datestamp in the filename."""
    try:
        # Regex pattern to find a sequence of exactly 14 digits (YYYYMMDDHHMMSS)
        matches = re.findall(r"\D?(\d{14})\D?", str(Path(filename).stem))
        if matches:
            return _convert_datestamp_to_epoch(matches[0])
        else:
            logger.error(f"No valid 14-digit datestamp found in {filename}")
            return None
    except ValueError as e:
        logger.error(f"Failed to extract datestamp from {filename}: {str(e)}")
        return None
