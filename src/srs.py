#!/usr/bin/env python3
import yaml
from pathlib import Path
from datetime import datetime, timedelta

# Load configuration
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

SRS_INTERVALS = cfg.get("srs_intervals", {
    1: 1,    # box 1 → 1 day
    2: 3,    # box 2 → 3 days
    3: 7,    # box 3 → 7 days
    4: 14,   # box 4 → 14 days
    5: 30    # box 5 → 30 days
})

def update_box(current_box: int, score: int) -> int:
    """
    Update a card's box based on the user's score (1-5).
    Returns the new box number.
    """
    if score >= 4:
        # Move up one box, but don't exceed box 5
        return min(current_box + 1, 5)
    elif score <= 2:
        # Move back to box 1
        return 1
    else:
        # Stay in the same box
        return current_box

def calculate_next_review(box: int) -> datetime:
    """
    Calculate the next review date based on the box number.
    """
    interval = SRS_INTERVALS.get(box, 1)  # Default to 1 day if box not found
    return datetime.now() + timedelta(days=interval)
