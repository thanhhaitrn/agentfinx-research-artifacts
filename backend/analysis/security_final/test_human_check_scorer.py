"""Scientific edge cases: no forced votes, exposure exclusions and independent kappa checks."""
import numpy as np
import pytest
from statsmodels.stats.inter_rater import cohens_kappa, fleiss_kappa

from analysis.security_final import human_check_scorer as h


@pytest.mark.parametrize("votes, expected", [
    (["true", "true", "false"], "true"),
    (["true", "false", "not_applicable"], None),
    (["true", "true", "unclear"], None),
    (["false", "false", None], None),
    (["false"], "false"), ([], None),
])
def test_majority_does_not_force_unclear_missing_or_tied(votes, expected):
    assert h.majority(votes) == expected


def test_exposure_is_excluded_without_changing_original_annotation():
    row = {"adopted_target": "true", "da_tung_xem": "co"}
    assert h.eligible_label(row, "adopted_target") is None
    assert row["adopted_target"] == "true"
    assert h.eligible_label({"adopted_target": "false", "da_tung_xem": None}, "adopted_target") == "false"


def test_fleiss_matches_statsmodels_for_three_categories():
    triples = [["a", "a", "b"], ["b", "b", "b"], ["a", "c", "c"], ["c", "a", "b"]]
    counts = np.array([[row.count(c) for c in ("a", "b", "c")] for row in triples])
    assert h.fleiss(triples) == pytest.approx(fleiss_kappa(counts))
    assert h.fleiss([["a", "a", "a"]]) is None


def test_cohen_matches_statsmodels_and_unclear_is_not_a_category():
    pairs = [("a", "a"), ("b", "a"), ("b", "b"), ("c", "c"), (None, "a"), ("unclear", "b")]
    table = np.array([[1, 0, 0], [1, 1, 0], [0, 0, 1]])
    result = h.agreement(pairs)
    assert result["items"] == 4 and result["excluded"] == 2
    assert result["kappa"] == pytest.approx(cohens_kappa(table).kappa)


def test_adoption_denominators_are_explicit_and_different():
    pairs = [("false", "false")]*8 + [("false", "true")]*2 + [("true", "true")]*3 + [("true", "false")]
    s = h.adoption_stats(pairs + [("false", None)])
    assert s["excluded"] == 1
    assert s["false_omission_rate"] == 2/10
    assert s["false_negative_rate"] == 2/5
    assert s["false_discovery_rate"] == 1/4
    assert s["false_positive_rate"] == 1/9


def test_xlsx_duplicate_ids_are_rejected(monkeypatch, tmp_path):
    class Sheet:
        def iter_rows(self, **kwargs):
            return iter([("item_id", "adopted_target"), ("R1H001", "true"), ("R1H001", "false")])
    class Book:
        worksheets = [Sheet()]
        def close(self):
            pass
    monkeypatch.setattr("openpyxl.load_workbook", lambda *a, **k: Book())
    with pytest.raises(ValueError, match="duplicate item_id"):
        h.read_xlsx(tmp_path / "fake.xlsx")
