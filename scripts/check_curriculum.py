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
        if not text.startswith("<!-- current-curriculum: 2026-09-22 -->"):
            errors.append(f"Not a current lesson: {current.relative_to(ROOT)}")
        for section in ["## 概念解說", "## 閱讀與練習", "## 舊版與新版本的關係"]:
            if section not in text:
                errors.append(f"Missing {section}: {current.relative_to(ROOT)}")
        # Every lesson embeds a reading excerpt and a matching read-only source command.
        source_match = re.search(r"sed -n '(\d+),(\d+)p' '([^']+)'", text)
        if not source_match:
            errors.append(f"Missing source exercise: {current.relative_to(ROOT)}")
        else:
            start, end, source = source_match.groups()
            expected = "\n".join(line.rstrip() for line in
                                 (ROOT / source).read_text().splitlines()[int(start)-1:int(end)])
            if expected not in text:
                errors.append(f"Stale source excerpt: {current.relative_to(ROOT)}")
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
    # Include all current docs and the archive index; .md.txt snapshots are raw text.
    pages.update((ROOT / "docs").rglob("*.md"))
    count = 0
    for page in sorted(pages):
        if not page.exists():
            continue
        try:
            text = prose_only(page.read_text())
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
    return {"passed": not errors, "lessons": len(records), "weekly_introductions": 20,
            "pages_checked": len(pages), "local_links_checked": count,
            "protected_evidence_files": len(manifest["protected_evidence_sha256"]),
            "errors": errors}


if __name__ == "__main__":
    report = check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["passed"] else 1)
