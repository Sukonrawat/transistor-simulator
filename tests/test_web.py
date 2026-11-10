"""HTTP tests for the Flask app via Flask's test client (ENG29 2121 · Lab 02).

Covers the browser-visible acceptance tests A1, A2, A4 and A5 without
starting a real server (see Flask docs: Testing Flask Applications).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make the project root importable no matter where unittest is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402

# Reference circuit from the lab handout, as submitted by a browser.
REFERENCE_FORM = {
    "vcc": "12",
    "r1": "100000",
    "r2": "22000",
    "rc": "2200",
    "re": "1000",
    "beta": "100",
    "vbe": "0.7",
}


class WebAppTest(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_a1_get_index_shows_the_input_form(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for field in REFERENCE_FORM:
            self.assertIn(f'name="{field}"', html)
        self.assertIn("BJT", html)
        # The form must post to the calculate route (backend computation).
        self.assertIn("/calculate", html)

    def test_a2_post_calculate_returns_backend_results(self):
        response = self.client.post("/calculate", data=REFERENCE_FORM)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        # Values computed by the Python backend (not hardcoded in HTML):
        self.assertIn("9.294", html)   # VC  [V]
        self.assertIn("8.052", html)   # VCE [V]
        self.assertIn("1.230", html)   # IC  [mA]
        self.assertIn("12.30", html)   # IB  [uA]

    def test_a3_post_root_route_behaves_like_calculate(self):
        response = self.client.post("/", data=REFERENCE_FORM)
        self.assertEqual(response.status_code, 200)
        self.assertIn("8.052", response.get_data(as_text=True))

    def test_a2_results_change_with_the_input(self):
        different = dict(REFERENCE_FORM)
        different["vcc"] = "9"
        response = self.client.post("/calculate", data=different)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        # For VCC = 9 V the old VCE 8.052 V must be gone (no hardcoded HTML).
        self.assertNotIn("8.052", html)

    def test_a4_negative_resistor_shows_clear_error(self):
        bad = dict(REFERENCE_FORM)
        bad["rc"] = "-5"
        response = self.client.post("/calculate", data=bad)
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        self.assertIn("RC", html)          # error names the offending field
        self.assertIn("มากกว่า 0", html)   # and explains the rule
        self.assertNotIn("8.052", html)    # no stale results table

    def test_a4_non_numeric_and_missing_shows_clear_error(self):
        bad = dict(REFERENCE_FORM)
        bad["vcc"] = "abc"
        bad["r2"] = ""
        response = self.client.post("/calculate", data=bad)
        self.assertEqual(response.status_code, 400)
        html = response.get_data(as_text=True)
        self.assertIn("VCC", html)
        self.assertIn("ตัวเลข", html)
        self.assertIn("R2", html)

    def test_a5_cutoff_case_shows_warning(self):
        form = {
            "vcc": "5", "r1": "10000", "r2": "100", "rc": "2000",
            "re": "500", "beta": "100", "vbe": "0.7",
        }
        response = self.client.post("/calculate", data=form)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Cutoff", html)
        self.assertIn("อยู่นอกสมมติฐาน Forward-Active", html)

    def test_a5_saturation_case_shows_warning(self):
        bad = dict(REFERENCE_FORM)
        bad["rc"] = "10000"
        response = self.client.post("/calculate", data=bad)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Saturation", html)
        self.assertIn("อยู่นอกสมมติฐาน Forward-Active", html)


if __name__ == "__main__":
    unittest.main()
