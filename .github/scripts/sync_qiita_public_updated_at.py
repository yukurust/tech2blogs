#!/usr/bin/env python3
"""
- 通常モード: qiita/public/*.md の本文がコミット間で変わったときだけ updated_at を揃える（push 後の別ジョブ用）。
- publish モード (QIITA_SYNC_MODE=publish): Qiita 送信直前に、対象ファイルの updated_at を
  トリガーコミット（AFTER_SHA）基準の git 時刻で上書きする。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ZERO = "0000000000000000000000000000000000000000"


def run_git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.check_output(["git", *args], cwd=cwd or REPO_ROOT, text=True)
    return out.strip()


def split_frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return None
    rest_start = m.end()
    return m.group(1), text[rest_start:]


def body_fingerprint(content: str) -> str | None:
    sp = split_frontmatter(content)
    if sp is None:
        return None
    _, body = sp
    return body


def git_show(commit: str, path: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "show", f"{commit}:{path}"],
            cwd=REPO_ROOT,
            text=True,
        )
    except subprocess.CalledProcessError:
        return None


def qiita_updated_at_from_git_iso(iso: str) -> str:
    s = iso.strip()
    if s.endswith("Z"):
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    ms = dt.microsecond // 1000
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{ms:03d}Z"


def last_commit_iso_for_path(rev: str, path: str) -> str:
    return run_git("log", "-1", "--format=%cI", rev, "--", path)


def last_commit_iso_for_path_or_tip(rev: str, path: str) -> str:
    r = subprocess.run(
        ["git", "log", "-1", "--format=%cI", rev, "--", path],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return run_git("log", "-1", "--format=%cI", rev)


def commit_iso_for_article_or_tip(rev: str, basename: str) -> str:
    ap = f"articles/{basename}.md"
    return last_commit_iso_for_path_or_tip(rev, ap)


def replace_updated_at(fm: str, new_val: str) -> str:
    line = f"updated_at: '{new_val}'"
    if re.search(r"(?m)^updated_at:\s*", fm):
        return re.sub(r"(?m)^updated_at:\s*.*$", line, fm, count=1)
    return fm.rstrip() + "\n" + line


def write_file_with_fm(path: Path, new_fm: str, rest_body: str) -> None:
    path.write_text("---\n" + new_fm + "\n---\n" + rest_body, encoding="utf-8")


def list_candidates(before: str, after: str) -> list[str]:
    if not before or before == ZERO:
        diff_base = ZERO
    else:
        diff_base = before
    raw = run_git("diff", "--name-only", diff_base, after)
    out: list[str] = []
    for p in raw.splitlines():
        if p.startswith("qiita/public/") and p.endswith(".md"):
            out.append(p)
    return sorted(set(out))


def bump_qiita_file_updated_at(qp_rel: str, iso_raw: str) -> None:
    path = REPO_ROOT / qp_rel
    q = qiita_updated_at_from_git_iso(iso_raw)
    text = path.read_text(encoding="utf-8")
    sp = split_frontmatter(text)
    if sp is None:
        print(f"pre-publish skip (no front matter): {qp_rel}", file=sys.stderr)
        return
    fm, rest_body = sp
    new_fm = replace_updated_at(fm, q)
    if new_fm == fm:
        return
    write_file_with_fm(path, new_fm, rest_body)
    print(f"pre-publish updated_at: {qp_rel} -> {q}")


def main_publish() -> int:
    """Qiita publish 直前: 送信対象の updated_at を AFTER_SHA に揃える。"""
    after = os.environ.get("AFTER_SHA", "").strip()
    if not after:
        print("AFTER_SHA is required", file=sys.stderr)
        return 1

    publish_all = os.environ.get("PUBLISH_ALL", "").strip().lower() in ("1", "true", "yes")
    targets_path = os.environ.get("TARGETS_FILE", "").strip()
    tp = Path(targets_path) if targets_path else None

    jobs: list[tuple[str, str]] = []

    if publish_all:
        pub = REPO_ROOT / "qiita/public"
        if not pub.is_dir():
            print("qiita/public not found", file=sys.stderr)
            return 0
        for path in sorted(p for p in pub.rglob("*.md") if p.is_file()):
            rel = path.relative_to(REPO_ROOT).as_posix()
            iso = last_commit_iso_for_path_or_tip(after, rel)
            jobs.append((rel, iso))
        print(f"pre-publish: --all 相当で {len(jobs)} 件の updated_at を揃えます")
    elif tp is not None and tp.is_file() and tp.stat().st_size > 0:
        basenames = sorted(
            {
                line.strip()
                for line in tp.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        )
        for basename in basenames:
            rel = f"qiita/public/{basename}.md"
            if not (REPO_ROOT / rel).is_file():
                print(f"pre-publish skip (missing file): {rel}", file=sys.stderr)
                continue
            iso = commit_iso_for_article_or_tip(after, basename)
            jobs.append((rel, iso))
        print(f"pre-publish: 対象 {len(jobs)} 件の updated_at を揃えます")
    else:
        print("pre-publish: 対象なし（ターゲット無し・--all ではない）。スキップします。")
        return 0

    for rel, iso in jobs:
        bump_qiita_file_updated_at(rel, iso)
    return 0


def main() -> int:
    mode = os.environ.get("QIITA_SYNC_MODE", "").strip().lower()
    if mode == "publish":
        return main_publish()

    before = os.environ.get("BEFORE_SHA", "").strip()
    after = os.environ.get("AFTER_SHA", "").strip()
    if not after:
        print("AFTER_SHA is required", file=sys.stderr)
        return 1

    if not before or before == ZERO:
        before_tree = ""
    else:
        before_tree = before

    candidates = list_candidates(before, after)
    if not candidates:
        print("No qiita/public/*.md in diff; nothing to do.")
        return 0

    wrote_any = False
    for rel in candidates:
        path = REPO_ROOT / rel
        if not path.is_file():
            continue
        new_text = path.read_text(encoding="utf-8")
        new_body = body_fingerprint(new_text)

        if before_tree:
            old_text = git_show(before_tree, rel)
        else:
            old_text = None
        old_body = body_fingerprint(old_text) if old_text is not None else None

        if old_body is not None and new_body is not None and old_body == new_body:
            print(f"skip (body unchanged): {rel}")
            continue

        iso = last_commit_iso_for_path(after, rel)
        q = qiita_updated_at_from_git_iso(iso)
        sp = split_frontmatter(new_text)
        if sp is None:
            print(f"skip (no front matter): {rel}", file=sys.stderr)
            continue

        fm, rest_body = sp
        new_fm = replace_updated_at(fm, q)
        if new_fm == fm:
            print(f"skip (updated_at already matches commit time): {rel}")
            continue

        write_file_with_fm(path, new_fm, rest_body)
        print(f"updated updated_at: {rel} -> {q}")
        wrote_any = True

    if not wrote_any:
        print("No updated_at changes applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
