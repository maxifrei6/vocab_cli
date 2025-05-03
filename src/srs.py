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

def update_box(cursor, word: str, correct: bool) -> int:
    """
    Update a card's box based on whether the answer was correct.
    Returns the new box number.
    """
    # Get current box
    cursor.execute("SELECT box FROM vocab WHERE word = ?", (word,))
    current_box = cursor.fetchone()[0]
    
    if correct:
        # Move up one box, but don't exceed box 5
        new_box = min(current_box + 1, 5)
    else:
        # Move back to box 1
        new_box = 1
    
    return new_box

def calculate_next_review(today: datetime.date, box: int) -> datetime.date:
    """
    Calculate the next review date based on the box number.
    """
    interval = SRS_INTERVALS.get(box, 1)  # Default to 1 day if box not found
    return today + timedelta(days=interval)
