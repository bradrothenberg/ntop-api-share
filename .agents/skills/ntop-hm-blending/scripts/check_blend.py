"""Portable algebra checks and regression against frozen native field samples."""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import unittest
from decimal import Decimal, localcontext

from blend_reference import (
    anchor_correction, compact_union, effective_weights, hm_average,
    linear_average,
)
from wing_example import fields, OFFSETS_MM, REFERENCE_LENGTH_MM

FIXTURE = Path(__file__).resolve().parents[1]/"assets/native_samples.json"


class BlendChecks(unittest.TestCase):
    def test_bounds_and_identical_fields(self):
        rng = random.Random(47)
        for _ in range(300):
            values = [rng.uniform(-20, 20) for _ in range(3)]
            weights = [rng.uniform(-2, 2) for _ in values]
            for p in (-80, -4, -1e-10, 0, 1e-10, 4, 80):
                value = hm_average(values, p, weights, 10)
                self.assertTrue(min(values)-1e-10 <= value <= max(values)+1e-10)
                self.assertEqual(hm_average([2.75]*3, p, weights, 10), 2.75)

    def test_mean_and_weight_direction(self):
        self.assertEqual(hm_average((2, 8), 0, (0, 100), 10), 5)
        self.assertEqual(linear_average((2, 8), 0, (0, 100)), 5)
        self.assertLess(effective_weights(-4, (0, 0.75))[1], 0.5)
        self.assertGreater(effective_weights(4, (0, 0.75))[1], 0.5)

    def test_small_p_against_high_precision(self):
        # Independent high-precision direct Eq.20 calculation.
        with localcontext() as context:
            context.prec = 70
            for p_text in ("-1e-12", "1e-12", "-0.01", "0.01"):
                p, length = Decimal(p_text), Decimal("10")
                values = (Decimal("-2"), Decimal("7"))
                weights = (Decimal("0.2"), Decimal("-0.6"))
                numerator = sum((p*(v/length+w)).exp()
                                for v, w in zip(values, weights))
                denominator = sum((p*w).exp() for w in weights)
                expected = float(length*(numerator/denominator).ln()/p)
                actual = hm_average((-2, 7), float(p), (0.2, -0.6), 10)
                self.assertAlmostEqual(actual, expected, delta=2e-12)

    def test_translation_scale_permutation_and_repetition(self):
        values, weights = (-3.0, 1.0, 8.0), (0.0, 0.3, -0.2)
        for p in (-20, -4, 0, 4, 20):
            base = hm_average(values, p, weights, 10)
            self.assertAlmostEqual(hm_average([v+100 for v in values], p,
                                             weights, 10), base+100, delta=1e-11)
            self.assertAlmostEqual(hm_average([v*1000 for v in values], p,
                                             weights, 10000), base*1000, delta=1e-9)
            self.assertAlmostEqual(hm_average(values[::-1], p, weights[::-1], 10),
                                   base, delta=1e-12)
            self.assertAlmostEqual(hm_average(values*2, p, weights*2, 10),
                                   base, delta=1e-12)

    def test_large_logits_stay_finite(self):
        for p in (-1000, 1000):
            value = hm_average((-100, 100), p, (0, 0.25), 0.1)
            self.assertTrue(math.isfinite(value))
            self.assertTrue(-100 <= value <= 100)

    def test_compact_support_and_anchors(self):
        self.assertEqual(compact_union(-2, 5, 0), -2)
        self.assertEqual(compact_union(-2, 5, 4), -2)
        self.assertAlmostEqual(compact_union(0, 0, 4), -0.75)
        # At each anchor the correction cancels that candidate's own residual.
        for top, bottom in ((-2, -0.5), (1.2, -3)):
            self.assertEqual(anchor_correction(top, top, bottom, 0, 17, 17, -17, 8), 0)
            self.assertEqual(anchor_correction(bottom, top, bottom, 0, -17, 17, -17, 8), 0)
        for offset in OFFSETS_MM.values():
            for x in (-20, 0, 20, 40, 60):
                crown = 17.5*math.sqrt(1-(x/92.5)**8)
                for z in (-crown, crown):
                    result = fields((x, 0, z), offset)
                    for name in ("small", "large", "single", "linear", "hm"):
                        self.assertAlmostEqual(result[name], 0, delta=1e-10)

    def test_reflected_upper_lower(self):
        for point in ((-5, 12, 14), (10, 20, 9), (40, -15, 10)):
            upper = fields(point, 10.5)
            lower = fields((point[0], point[1], -point[2]), -10.5)
            for name in upper:
                self.assertAlmostEqual(upper[name], lower[name], delta=1e-10)

    def test_invalid_parameters(self):
        for args in (((), 1, None, 1), ((1, 2), 1, (0,), 1),
                     ((1, 2), 1, None, 0), ((math.nan, 2), 1, None, 1),
                     ((1, 2), math.inf, None, 1)):
            with self.assertRaises(ValueError):
                hm_average(*args)
        with self.assertRaises(ValueError):
            compact_union(1, 2, -1)
        with self.assertRaises(ValueError):
            anchor_correction(0, 0, 0, 0, 0, 1, 1, 8)

    def test_frozen_native_samples(self):
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        maximum, count = 0.0, 0
        self.assertEqual(set(fixture["cases"]), set(OFFSETS_MM))
        for position, case in fixture["cases"].items():
            self.assertEqual(case["offset_mm"], OFFSETS_MM[position])
            self.assertEqual(len(case["samples"]), 90)
            for row in case["samples"]:
                actual = fields(row["point_mm"], case["offset_mm"])[row["field"]]
                actual /= REFERENCE_LENGTH_MM
                error = abs(actual-row["native_normalized"])
                with self.subTest(position=position, name=row["name"]):
                    self.assertLess(error, fixture["normalized_tolerance"])
                maximum, count = max(maximum, error), count+1
        print(f"Frozen native samples: {count}; maximum normalized error: {maximum:.6g}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
