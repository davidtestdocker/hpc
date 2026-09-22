"""唯讀驗證現行教材：目錄、連結、舊版 SHA-256 與原始證據保留。

不連叢集、不執行教材命令、不修改 snapshots。從 repo 任意位置執行皆可。
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs/history/20260922-before-current"


def prose_only(text):
    """移除 fenced code，避免把來源片段內的範例連結當作頁面導航。"""
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append(line)
    if fence is not None:
        raise ValueError("Unclosed code fence")
    return "\n".join(result)


def anchors(text):
    result = set(re.findall(r'<a\s+id="([^"]+)"', text))
    # Only the new reading section is audited as current navigation.
    text = text.split('<!-- original-week-body -->', 1)[0]
    for heading in re.findall(r"^#{1,6}\s+(.+)$", prose_only(text), re.MULTILINE):
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        result.add(slug)
    return result


def check():
    errors = []
    manifest = json.loads((ARCHIVE / "manifest.json").read_text())
    records = manifest["files"]
    if len(records) != 138:
        errors.append(f"Expected 138 archived lessons, found {len(records)}")
    pages = {ROOT / record["source"] for record in records}
    for record in records:
        archived = ROOT / record["archive"]
        data = archived.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            errors.append(f"Archive changed: {archived.relative_to(ROOT)}")
        current = ROOT / record["source"]
        text = current.read_text()
        if not text.startswith("<!-- readable-curriculum: 2026-09-22 -->"):
            errors.append(f"Not a current lesson: {current.relative_to(ROOT)}")
        for section in ["## 概念解說", "## 已有結果與解讀", "## 原始完整教材與當時輸出"]:
            if section not in text:
                errors.append(f"Missing {section}: {current.relative_to(ROOT)}")
        # The original detailed lesson is directly in the original .md, byte-identical.
        marker = '<!-- original-week-body -->\n'
        if marker not in text:
            errors.append(f"Missing full original lesson: {current.relative_to(ROOT)}")
        else:
            body = text.split(marker, 1)[1].encode()
            if (len(body) != record['original_body_bytes']
                    or hashlib.sha256(body).hexdigest() != record['original_body_sha256']):
                errors.append(f"Original body changed: {current.relative_to(ROOT)}")
        if archived.suffix != '.md':
            errors.append(f"Archive is not Markdown: {archived}")
    if list(ARCHIVE.rglob('*.md.txt')):
        errors.append('Text-only Markdown archives still present')
    for name, digest in manifest["protected_evidence_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            errors.append(f"Raw evidence changed: {name}")
    for n in range(1, 21):
        page = ROOT / f"docs/week{n}/README.md"
        if not page.is_file():
            errors.append(f"Missing weekly introduction: {n}")
        pages.add(page)
    pages.update({ROOT / "README.md", ROOT / "docs/learning-guide.md",
                  ROOT / "docs/current-environment.md", ARCHIVE / "README.md"})
    # Audit current navigation; historical Markdown has preserved legacy syntax.
    pages.update(p for p in (ROOT / "docs").rglob("*.md")
                 if not p.is_relative_to(ARCHIVE) or p.name == 'README.md')
    count = 0
    for page in sorted(pages):
        if not page.exists():
            continue
        try:
            text = prose_only(page.read_text().split('<!-- original-week-body -->', 1)[0])
        except ValueError as exc:
            errors.append(f"{page.relative_to(ROOT)}: {exc}")
            continue
        for match in re.finditer(r"\]\((<[^>]+>|[^)\s]+)\s*\)", text):
            target = match[1].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            destination = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
            count += 1
            if not destination.exists():
                errors.append(f"Broken link: {page.relative_to(ROOT)} -> {target}")
            elif (parsed.fragment and destination.suffix == ".md"
                  and unquote(parsed.fragment) not in anchors(destination.read_text())):
                errors.append(f"Broken anchor: {page.relative_to(ROOT)} -> {target}")
    # Structural success must never be presented as a complete content review.
    audit_path = ROOT / "docs/audits/curriculum-content-audit.json"
    reviewed = 0
    if audit_path.exists():
        audit = json.loads(audit_path.read_text())
        entries = audit["lessons"]
        expected = {record["source"] for record in records}
        if len(entries) != len(expected) or {entry["source"] for entry in entries} != expected:
            errors.append("Content audit ledger does not match lesson inventory")
        for entry in entries:
            if entry["status"] not in {"reviewed", "pending"}:
                errors.append(f"Unknown audit status: {entry['source']}")
            if entry["status"] == "reviewed":
                reviewed += 1
                for field in ("evidence_kind", "evidence_source", "excerpt", "interpretation",
                              "corrections", "missing", "reviewed_at", "scope"):
                    if not entry.get(field):
                        errors.append(f"Reviewed lesson missing {field}: {entry['source']}")
                source = ROOT / entry.get("evidence_source", "")
                if not source.is_file():
                    errors.append(f"Missing excerpt source: {entry['source']}")
                else:
                    source_text = source.read_text()
                    # Do not validate an excerpt against our own inserted copy.
                    source_text = source_text.split('<!-- original-week-body -->\n', 1)[-1]
                    if entry.get("excerpt", "") not in source_text:
                        errors.append(f"Excerpt not present in original source: {entry['source']}")
                if set(entry.get("checked_files", [])) != set(entry.get("reviewed_files_sha256", {})):
                    errors.append(f"Implementation hash coverage mismatch: {entry['source']}")
                for name, digest in entry.get("reviewed_files_sha256", {}).items():
                    path = ROOT / name
                    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                        errors.append(f"Reviewed implementation changed; re-review required: {name}")
    return {"passed": not errors, "scope": "structure_links_and_preservation_only",
            "content_reviewed": reviewed, "content_pending": len(records) - reviewed,
            "lessons": len(records), "weekly_introductions": 20,
            "pages_checked": len(pages), "local_links_checked": count,
            "protected_evidence_files": len(manifest["protected_evidence_sha256"]),
            "errors": errors}


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
