import hashlib
import shutil
import unittest
from dataclasses import replace
from pathlib import Path

from PROJECT_INCUBATOR.runtime.adapters.file_store import (
    FileSnapshot,
    FileStore,
    FileVerificationError,
    FileWriteError,
)


class FileStoreSnapshotTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent / ".tmp_file_store"
        shutil.rmtree(self.root, ignore_errors=True)
        self.root.mkdir(parents=True)
        self.store = FileStore(self.root)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_restore_existing_file_uses_original_content_and_verifies_readback(self):
        path = self.root / "PROJECT_PLAN.md"
        path.write_text("before", encoding="utf-8")
        snapshot = self.store.snapshot("PROJECT_PLAN.md")
        self.store.atomic_write("PROJECT_PLAN.md", "after")

        result = self.store.restore(snapshot)

        self.assertTrue(result.verified)
        self.assertEqual("before", path.read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(b"before").hexdigest(), snapshot.digest)

    def test_restore_removes_file_created_after_absent_snapshot(self):
        snapshot = self.store.snapshot("CAPABILITY_SPIRAL_RECORD.md")
        self.store.atomic_write("CAPABILITY_SPIRAL_RECORD.md", "created")

        result = self.store.restore(snapshot)

        self.assertIsNone(result)
        self.assertFalse((self.root / "CAPABILITY_SPIRAL_RECORD.md").exists())

    def test_restore_rejects_snapshot_with_content_digest_mismatch(self):
        path = self.root / "PROJECT_STATE.md"
        path.write_text("before", encoding="utf-8")
        snapshot = replace(self.store.snapshot("PROJECT_STATE.md"), digest="0" * 64)
        self.store.atomic_write("PROJECT_STATE.md", "after")

        with self.assertRaisesRegex(FileVerificationError, "snapshot digest mismatch"):
            self.store.restore(snapshot)

        self.assertEqual("after", path.read_text(encoding="utf-8"))

    def test_restore_propagates_atomic_write_failure(self):
        path = self.root / "PROJECT_STATE.md"
        path.write_text("before", encoding="utf-8")
        snapshot = self.store.snapshot("PROJECT_STATE.md")
        path.write_text("after", encoding="utf-8")
        failing = FailingRestoreFileStore(self.root)

        with self.assertRaisesRegex(FileWriteError, "injected restore failure"):
            failing.restore(snapshot)

        self.assertEqual("after", path.read_text(encoding="utf-8"))


class FailingRestoreFileStore(FileStore):
    def atomic_write(self, path, content):
        raise FileWriteError("injected restore failure")


if __name__ == "__main__":
    unittest.main()
