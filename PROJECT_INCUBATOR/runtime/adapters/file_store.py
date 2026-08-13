"""Controlled file I/O adapter for Project Incubator V1 runtime."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path


class FileStoreError(Exception):
    """Base exception for File Store Adapter failures."""


class FileReadError(FileStoreError):
    """Raised when a file cannot be read."""


class FileWriteError(FileStoreError):
    """Raised when a file write operation cannot be completed."""


class FileVerificationError(FileStoreError):
    """Raised when read-back verification fails after a write."""


@dataclass(frozen=True)
class FileWriteResult:
    path: Path
    bytes_written: int
    verified: bool


class FileStore:
    """Provides deterministic file operations without domain authorization logic."""

    def __init__(self, base_dir: str | Path | None = None, encoding: str = "utf-8") -> None:
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else None
        self.encoding = encoding

    def exists(self, path: str | Path) -> bool:
        return self._resolve_path(path).exists()

    def read_file(self, path: str | Path) -> str:
        resolved_path = self._resolve_path(path)
        try:
            return resolved_path.read_text(encoding=self.encoding)
        except OSError as exc:
            raise FileReadError(f"failed to read file: {resolved_path}") from exc

    def atomic_write(self, path: str | Path, content: str) -> FileWriteResult:
        resolved_path = self._resolve_path(path)
        encoded_content = content.encode(self.encoding)
        temp_path: Path | None = None

        try:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "wb",
                delete=False,
                dir=resolved_path.parent,
                prefix=f".{resolved_path.name}.",
                suffix=".tmp",
            ) as temp_file:
                temp_file.write(encoded_content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                temp_path = Path(temp_file.name)

            os.replace(temp_path, resolved_path)
        except OSError as exc:
            if temp_path is not None:
                self._remove_temp_file(temp_path)
            raise FileWriteError(f"failed to atomically write file: {resolved_path}") from exc

        self._verify_content(resolved_path, content)
        return FileWriteResult(
            path=resolved_path,
            bytes_written=len(encoded_content),
            verified=True,
        )

    def append(self, path: str | Path, content: str) -> FileWriteResult:
        resolved_path = self._resolve_path(path)
        previous_content = self.read_file(resolved_path) if resolved_path.exists() else ""
        next_content = previous_content + content

        try:
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            with resolved_path.open("a", encoding=self.encoding) as file_handle:
                file_handle.write(content)
                file_handle.flush()
                os.fsync(file_handle.fileno())
        except OSError as exc:
            raise FileWriteError(f"failed to append file: {resolved_path}") from exc

        self._verify_content(resolved_path, next_content)
        return FileWriteResult(
            path=resolved_path,
            bytes_written=len(content.encode(self.encoding)),
            verified=True,
        )

    def _resolve_path(self, path: str | Path) -> Path:
        raw_path = Path(path)
        if raw_path.is_absolute():
            return raw_path
        if self.base_dir is not None:
            return self.base_dir / raw_path
        return raw_path

    def _verify_content(self, path: Path, expected_content: str) -> None:
        try:
            actual_content = path.read_text(encoding=self.encoding)
        except OSError as exc:
            raise FileVerificationError(f"failed to read back file: {path}") from exc

        if actual_content != expected_content:
            raise FileVerificationError(f"read-back verification failed: {path}")

    @staticmethod
    def _remove_temp_file(path: Path) -> None:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


__all__ = [
    "FileReadError",
    "FileStore",
    "FileStoreError",
    "FileVerificationError",
    "FileWriteError",
    "FileWriteResult",
]
