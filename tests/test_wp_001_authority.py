"""WP-001 authority guard tests; not an independent audit or ratification."""

import copy
import unittest
from pathlib import Path

from axiomlint.governance import check
from axiomlint.schema import InvalidRecord, load_json, validate

ROOT = Path(__file__).resolve().parents[1]


class AuthorityRecordTests(unittest.TestCase):
    def setUp(self):
        self.record = load_json(ROOT / "governance/decisions/delegated-authority.json")
        self.schema = load_json(ROOT / "schemas/delegated-authority.schema.json")

    def test_user_grant_has_a_valid_record(self):
        validate(self.record, self.schema)

    def test_authority_quote_is_not_an_invented_signature(self):
        note = (ROOT / self.record["authority_evidence"]).read_text()
        self.assertIn(self.record["user_statement"], note)
        self.assertIn("not an invented signature", note)

    def test_routine_scope_and_reserved_decisions_are_disjoint(self):
        self.assertFalse(set(self.record["immediate_scope"]) & set(self.record["not_implied"]))

    def test_record_cannot_be_promoted_to_ratification(self):
        value = {**self.record, "ratification": "APPROVED"}
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_record_cannot_grant_author_self_approval(self):
        value = copy.deepcopy(self.record)
        value["immediate_scope"].append("AUTHOR_SELF_APPROVAL")
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_independence_reservation_cannot_be_removed(self):
        value = copy.deepcopy(self.record)
        value["not_implied"].remove("INDEPENDENT_AUDIT_OR_PROTOCOL_REVIEW")
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_scientific_condition_cannot_be_removed(self):
        value = copy.deepcopy(self.record)
        value["conditions"].remove("RIGOROUS_SCIENTIFIC_REASONING")
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_hosted_check_prohibition_cannot_be_removed(self):
        value = copy.deepcopy(self.record)
        value["conditions"].remove("LOCAL_ONLY_TESTS_NO_HOSTED_CI")
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_principal_cannot_be_impersonated_as_the_delegate(self):
        value = {**self.record, "delegate": "Michael Maillet"}
        with self.assertRaises(InvalidRecord):
            validate(value, self.schema)

    def test_unknown_authority_field_fails_closed(self):
        with self.assertRaises(InvalidRecord):
            validate({**self.record, "skip_s2": True}, self.schema)

    def test_author_review_is_labeled_not_s2(self):
        content = (ROOT / "governance/reviews/WP-001-charter-adoption-review.md").read_text()
        self.assertIn("AUTHOR REVIEW, NOT INDEPENDENT S2", content)

    def test_delegation_does_not_break_governance_structure(self):
        self.assertEqual(check(ROOT), [])

