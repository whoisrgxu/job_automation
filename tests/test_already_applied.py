import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from test import already_applied

TRACKER_PATH = "/Users/Roger/Documents/FullTime-Resume/Job Tracker.xlsx"
SHEET_NAME = "Job Tracker"

# Update the tuples below so they reflect real rows in the tracker.
# expected=True  => application exists within ~2 months
# expected=False => application either absent or older than ~2 months
TEST_CASES = [
    ("Scotiabank", "Test Automation Engineer", True),
    ("Broadridge", "Associate Software Engineer (Hybrid)", False),
    ("TD Bank", "QA Automation Developer", False),
    ("RBC", "Software Developer", False),
    ("Manulife", "Associate AI Engineer", True),
    ("Modall", "Frontend Developer (React/Next.js)", False),
]


@pytest.mark.parametrize("company, position, expected", TEST_CASES)
def test_already_applied_cases(company: str, position: str, expected: bool):
    assert already_applied(TRACKER_PATH, SHEET_NAME, company, position) is expected
