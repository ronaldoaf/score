import unittest

from scripts.analyze_copy_score import (
    average_ranks,
    extract_rows,
    make_report,
    quantile,
    spearman,
)


class AnalyzeCopyScoreTests(unittest.TestCase):
    def test_average_ranks_preserves_ties(self):
        self.assertEqual(average_ranks([10, 20, 20, 40]), [1.0, 2.5, 2.5, 4.0])

    def test_spearman_handles_ties(self):
        self.assertAlmostEqual(spearman([1, 2, 2, 4], [10, 20, 20, 40]), 1.0)

    def test_quantile_interpolates(self):
        self.assertEqual(quantile([1, 2, 3, 4], 0.5), 2.5)

    def test_extract_rows_accepts_graphql_wrapper(self):
        rows = [{"address": "0x1"}]
        self.assertEqual(extract_rows({"data": {"getSystemGroupTraders": rows}}), rows)

    def test_report_keeps_null_distinct_from_zero(self):
        rows = [
            {"copyScore": 0, "copyScoreV2": None, "tag": "algo"},
            {"copyScore": 0, "copyScoreV2": 10, "tag": "swing"},
            {"copyScore": 90, "copyScoreV2": 0, "tag": "algo"},
            {"copyScore": 50, "copyScoreV2": 20, "tag": "swing"},
        ]
        report = make_report(rows, "sample.json")
        self.assertIn("`copyScoreV2` nulo | 1", report)
        self.assertIn("`copyScoreV2` exatamente zero | 1", report)
        self.assertIn("`copyScore = 0` e `copyScoreV2 > 0`: **1** casos.", report)
        self.assertIn("`copyScore > 0` e `copyScoreV2 = 0`: **1** casos.", report)


if __name__ == "__main__":
    unittest.main()
