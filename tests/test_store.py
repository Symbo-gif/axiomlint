import os
import tempfile
import unittest
from pathlib import Path

from axiomlint.evidence.store import ArtifactStore, IntegrityError, canonical_json, sha256


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "store"
        self.store = ArtifactStore(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip_and_idempotence(self):
        digest = self.store.put(b"counterexample")
        self.assertEqual(self.store.get(digest), b"counterexample")
        self.assertEqual(self.store.put(b"counterexample"), digest)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_empty_content_is_a_real_artifact(self):
        digest = self.store.put(b"")
        self.assertEqual(self.store.get(digest), b"")

    def test_corrupt_read_fails(self):
        digest = self.store.put(b"original")
        path = self.root / digest
        path.chmod(0o644)
        path.write_bytes(b"modified")
        with self.assertRaises(IntegrityError):
            self.store.get(digest)

    def test_corrupt_preexisting_put_fails_without_overwrite(self):
        digest = sha256(b"expected")
        (self.root / digest).write_bytes(b"poisoned")
        with self.assertRaises(IntegrityError):
            self.store.put(b"expected")
        self.assertEqual((self.root / digest).read_bytes(), b"poisoned")

    def test_missing_artifact_fails(self):
        with self.assertRaises(IntegrityError):
            self.store.get("0" * 64)

    def test_digest_path_traversal_and_uppercase_fail(self):
        for digest in ("../secrets", "/etc/passwd", "A" * 64, "x" * 64, ""):
            with self.assertRaises(IntegrityError):
                self.store.get(digest)

    def test_symlink_artifact_fails(self):
        target = Path(self.tmp.name) / "target"
        target.write_bytes(b"expected")
        digest = sha256(b"expected")
        (self.root / digest).symlink_to(target)
        with self.assertRaises(IntegrityError):
            self.store.get(digest)
        with self.assertRaises(IntegrityError):
            self.store.put(b"expected")

    def test_symlink_store_parent_fails(self):
        real = Path(self.tmp.name) / "real"
        real.mkdir()
        link = Path(self.tmp.name) / "link"
        link.symlink_to(real, target_is_directory=True)
        with self.assertRaises(IntegrityError):
            ArtifactStore(link / "store")

    def test_fifo_artifact_rejected_without_blocking(self):
        digest = sha256(b"expected")
        os.mkfifo(self.root / digest)
        with self.assertRaises(IntegrityError):
            self.store.get(digest)

    def test_canonical_order_and_unicode(self):
        self.assertEqual(
            canonical_json({"b": 2, "a": "λ"}),
            canonical_json({"a": "λ", "b": 2}),
        )
        self.assertTrue(canonical_json({"a": 1}).endswith(b"\n"))
        self.assertIn("λ".encode(), canonical_json({"a": "λ"}))

    def test_nonfinite_serialization_rejected(self):
        for value in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                canonical_json({"value": value})

    def test_record_store_roundtrip(self):
        digest = self.store.put_record({"status": "UNKNOWN", "assumptions": ["x>=0"]})
        self.assertEqual(
            self.store.get(digest),
            canonical_json({"assumptions": ["x>=0"], "status": "UNKNOWN"}),
        )

