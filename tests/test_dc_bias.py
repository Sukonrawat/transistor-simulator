"""Unit tests for the dc_bias engineering module (ENG29 2121 · Lab 02).

The expected numbers in this file were computed by hand from the lab
reference circuit BEFORE the module was run, so they act as an
independent check of the engineering math (acceptance test A3).
The full step-by-step walkthrough lives in docs/validation.md.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Make the project root importable no matter where unittest is launched from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dc_bias  # noqa: E402

# Reference circuit from the lab handout (resistances in ohm).
REFERENCE = {
    "vcc": 12.0,
    "r1": 100_000.0,
    "r2": 22_000.0,
    "rc": 2_200.0,
    "re": 1_000.0,
    "beta": 100.0,
    "vbe": 0.70,
}


class ReferenceCircuitTest(unittest.TestCase):
    """A3: the reference circuit must match the independent hand calculation."""

    def test_reference_operating_point(self):
        result = dc_bias.calculate_dc_bias(**REFERENCE)
        # Hand calculation (independent, see docs/validation.md):
        #   VTH = 12 * 22k / (100k + 22k)         = 2.163934 V
        #   RTH = 100k * 22k / 122k               = 18032.787 ohm
        #   IB  = (VTH - 0.7) / (RTH + 101 * 1k)  = 1.2298581e-5 A
        #   IC  = 100 * IB                        = 1.2298581 mA
        #   IE  = 101 * IB                        = 1.2421567 mA
        #   VE  = IE * 1k                         = 1.2421567 V
        #   VB  = VE + 0.7                         = 1.9421567 V
        #   VC  = 12 - IC * 2.2k                  = 9.2943121 V
        #   VCE = VC - VE                         = 8.0521554 V
        self.assertAlmostEqual(result.vth, 2.1639344262295084, places=12)
        self.assertAlmostEqual(result.rth, 18032.786885245903, places=6)
        self.assertAlmostEqual(result.ib, 1.2298581462608458e-05, places=18)
        self.assertAlmostEqual(result.ic, 1.2298581462608458e-03, places=18)
        self.assertAlmostEqual(result.ie, 1.2421567277234543e-03, places=18)
        self.assertAlmostEqual(result.ve, 1.2421567277234544, places=12)
        self.assertAlmostEqual(result.vb, 1.9421567277234544, places=12)
        self.assertAlmostEqual(result.vc, 9.29431207822614, places=12)
        self.assertAlmostEqual(result.vce, 8.052155350502685, places=12)
        self.assertEqual(result.region, "forward-active")
        self.assertTrue(result.approximation_valid)
        self.assertEqual(result.warnings, ())

    def test_internal_consistency_of_the_model(self):
        """KCL / KVL identities that must hold for any valid solution."""
        result = dc_bias.calculate_dc_bias(**REFERENCE)
        self.assertAlmostEqual(result.ie, result.ib + result.ic, places=18)
        self.assertAlmostEqual(result.vb, result.ve + result.vbe, places=18)
        self.assertAlmostEqual(result.vce, result.vc - result.ve, places=18)
        self.assertAlmostEqual(result.ic, result.beta * result.ib, places=18)
        self.assertAlmostEqual(result.ic_ma, result.ic * 1e3, places=18)
        self.assertAlmostEqual(result.ib_ua, result.ib * 1e6, places=12)


class RegionAndWarningTest(unittest.TestCase):
    """A5: cutoff and saturation must be detected and warned about."""

    def test_cutoff_when_vth_below_vbe(self):
        # VTH = 5 * 100 / (10k + 100) = 0.495 V <= VBE = 0.7 V -> transistor off.
        result = dc_bias.calculate_dc_bias(
            vcc=5.0, r1=10_000.0, r2=100.0, rc=2_000.0, re=500.0, beta=100.0, vbe=0.7
        )
        self.assertEqual(result.region, "cutoff")
        self.assertFalse(result.approximation_valid)
        self.assertEqual(result.ib, 0.0)
        self.assertEqual(result.ic, 0.0)
        self.assertEqual(result.ie, 0.0)
        self.assertEqual(result.ve, 0.0)
        self.assertEqual(result.vb, result.vth)
        self.assertEqual(result.vc, 5.0)  # no current through RC
        self.assertEqual(result.vce, 5.0)  # whole supply across C-E
        self.assertTrue(any("Cutoff" in w for w in result.warnings))

    def test_saturation_when_vce_below_threshold(self):
        # Reference circuit with RC = 10 kOhm: VC = 12 - IC * 10k < VE.
        values = dict(REFERENCE)
        values["rc"] = 10_000.0
        result = dc_bias.calculate_dc_bias(**values)
        self.assertEqual(result.region, "saturation")
        self.assertFalse(result.approximation_valid)
        self.assertLess(result.vce, dc_bias.VCE_SAT_THRESHOLD)
        self.assertTrue(any("Saturation" in w for w in result.warnings))

    def test_near_saturation_still_active_but_warned(self):
        # Reference circuit with RC = 8.5 kOhm: VCE ~ 0.304 V -> forward-active
        # but close to the saturation edge, which must produce a warning.
        values = dict(REFERENCE)
        values["rc"] = 8_500.0
        result = dc_bias.calculate_dc_bias(**values)
        self.assertEqual(result.region, "forward-active")
        self.assertTrue(result.approximation_valid)
        self.assertGreaterEqual(result.vce, dc_bias.VCE_SAT_THRESHOLD)
        self.assertLess(result.vce, dc_bias.VCE_NEAR_SATURATION)
        self.assertTrue(any("Saturation" in w for w in result.warnings))


class InputValidationTest(unittest.TestCase):
    """A4: invalid component values must be rejected with clear messages."""

    def test_non_positive_values_are_rejected(self):
        cases = (("vcc", 0.0), ("vcc", -5.0), ("r1", 0.0), ("r1", -100.0),
                 ("r2", -1.0), ("rc", 0.0), ("re", -2.0), ("beta", 0.0), ("beta", -3.0))
        for name, value in cases:
            with self.subTest(field=name, value=value):
                values = dict(REFERENCE)
                values[name] = value
                with self.assertRaises(dc_bias.BiasInputError):
                    dc_bias.calculate_dc_bias(**values)

    def test_negative_vbe_is_rejected(self):
        values = dict(REFERENCE)
        values["vbe"] = -0.7
        with self.assertRaises(dc_bias.BiasInputError):
            dc_bias.calculate_dc_bias(**values)

    def test_parse_form_rejects_non_numeric_and_missing_fields(self):
        form = {
            "vcc": "12", "r1": "abc", "r2": "", "rc": "2200",
            "re": "1000", "beta": "100", "vbe": "0.7",
        }
        with self.assertRaises(dc_bias.BiasInputError) as ctx:
            dc_bias.parse_bias_form(form)
        # Both problems (R1 non-numeric, R2 missing) must be reported at once.
        self.assertEqual(len(ctx.exception.messages), 2)
        self.assertIn("R1", ctx.exception.messages[0])
        self.assertIn("R2", ctx.exception.messages[1])

    def test_parse_form_rejects_non_finite_values(self):
        for bad in ("inf", "-inf", "nan"):
            with self.subTest(value=bad):
                form = {k: str(v) for k, v in REFERENCE.items()}
                form["beta"] = bad
                with self.assertRaises(dc_bias.BiasInputError):
                    dc_bias.parse_bias_form(form)

    def test_parse_form_accepts_the_reference_circuit(self):
        form = {k: str(v) for k, v in REFERENCE.items()}
        values = dc_bias.parse_bias_form(form)
        self.assertEqual(set(values), set(dc_bias.FIELDS))
        self.assertAlmostEqual(values["rc"], 2200.0)
        self.assertAlmostEqual(values["vbe"], 0.70)


if __name__ == "__main__":
    unittest.main()
