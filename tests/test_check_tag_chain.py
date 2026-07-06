"""Tests for scripts/check_tag_chain.py (pre-commit TAG-chain backstop).

Covers the standard @SPEC -> @TEST -> @CODE wiring rules and the /ms.fix
track exemption: FIX-* @CODE ids carry no governing spec, so they are exempt
from the same-id @SPEC anchor requirement; @TEST stays required unless the
file declares a presentational marker.

Anchor strings in fixtures are built via ``tag()``/``marker()`` so this test
file itself never contains literal anchors — the backstop scans ``tests/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "scripts" / "check_tag_chain.py"
_spec = importlib.util.spec_from_file_location("check_tag_chain", MODULE_PATH)
assert _spec and _spec.loader
chain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(chain)


def tag(kind: str, tag_id: str) -> str:
    """Build an anchor line without embedding a literal anchor in this file."""
    return f"# @{kind}:{tag_id}\n"


def marker() -> str:
    """The presentational-fix marker line, assembled indirectly."""
    return "# @" + "TEST: (presentational — no test)\n"


def write(root: Path, relpath: str, text: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_empty_tree_passes(tmp_path: Path) -> None:
    assert chain.main(tmp_path) == 0


def test_wired_chain_passes(tmp_path: Path) -> None:
    write(tmp_path, "specs/001-auth/spec.md", tag("SPEC", "AUTH-001"))
    write(tmp_path, "tests/test_auth.py", tag("TEST", "AUTH-001"))
    write(tmp_path, "backend/auth.py", tag("CODE", "AUTH-001"))
    assert chain.main(tmp_path) == 0


def test_code_without_spec_fails(tmp_path: Path) -> None:
    write(tmp_path, "tests/test_auth.py", tag("TEST", "AUTH-001"))
    write(tmp_path, "backend/auth.py", tag("CODE", "AUTH-001"))
    assert chain.main(tmp_path) == 1


def test_code_without_test_fails(tmp_path: Path) -> None:
    write(tmp_path, "specs/001-auth/spec.md", tag("SPEC", "AUTH-001"))
    write(tmp_path, "backend/auth.py", tag("CODE", "AUTH-001"))
    assert chain.main(tmp_path) == 1


def test_duplicate_code_id_fails(tmp_path: Path) -> None:
    write(tmp_path, "specs/001-auth/spec.md", tag("SPEC", "AUTH-001"))
    write(tmp_path, "tests/test_auth.py", tag("TEST", "AUTH-001"))
    write(tmp_path, "backend/a.py", tag("CODE", "AUTH-001"))
    write(tmp_path, "backend/b.py", tag("CODE", "AUTH-001"))
    assert chain.main(tmp_path) == 1


def test_fix_id_without_spec_passes(tmp_path: Path) -> None:
    """/ms.fix track: FIX-* ids have no governing spec by design."""
    write(tmp_path, "backend/uploads.py", tag("CODE", "FIX-UPLOADS-003"))
    write(tmp_path, "tests/test_uploads.py", tag("TEST", "FIX-UPLOADS-003"))
    assert chain.main(tmp_path) == 0


def test_fix_id_without_test_fails(tmp_path: Path) -> None:
    write(tmp_path, "backend/uploads.py", tag("CODE", "FIX-UPLOADS-003"))
    assert chain.main(tmp_path) == 1


def test_fix_id_presentational_marker_exempts_test(tmp_path: Path) -> None:
    """A presentational fix declares the missing test explicitly."""
    write(tmp_path, "frontend/button.css.ts", tag("CODE", "FIX-STYLE-001") + marker())
    assert chain.main(tmp_path) == 0


def test_fix_id_duplicate_still_fails(tmp_path: Path) -> None:
    write(tmp_path, "backend/a.py", tag("CODE", "FIX-X-001") + marker())
    write(tmp_path, "backend/b.py", tag("CODE", "FIX-X-001") + marker())
    assert chain.main(tmp_path) == 1


def test_presentational_marker_does_not_exempt_normal_ids(tmp_path: Path) -> None:
    write(tmp_path, "backend/auth.py", tag("CODE", "AUTH-001") + marker())
    write(tmp_path, "specs/001-auth/spec.md", tag("SPEC", "AUTH-001"))
    assert chain.main(tmp_path) == 1
