#!/usr/bin/env python3
"""Static validation of the qa-agentic-pipeline plugin.

Checks the things that break a plugin silently: malformed frontmatter, a skill whose
name doesn't match its directory, an agent that preloads a skill that doesn't exist,
a "Related" link to a skill this plugin doesn't ship, a reference file that was never
written, an attribution notice out of sync with the adapted skills, and drift between
the artifact contract and the skills that implement it.

Usage:
    python tools/validate_plugin.py [plugin_root] [--json]

Exit code 0 when every check passes, 1 otherwise. No network, no model calls.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebFetch", "WebSearch",
    "Skill", "Agent", "TodoWrite", "NotebookEdit", "AskUserQuestion",
}
# Skills that exist in the upstream library (petrkindlmann/qa-skills) but are NOT
# shipped here. A reference to one of them is a dangling link left over from vendoring.
UPSTREAM_ONLY_SKILLS = {
    "test-strategy", "release-readiness", "qa-metrics", "qa-start", "exploratory-testing",
    "ci-cd-integration", "coverage-analysis", "shift-left-testing", "contract-testing",
    "visual-testing", "accessibility-testing", "test-reliability", "selector-drift-recovery",
    "compliance-testing", "ai-system-testing", "test-data-management", "test-environments",
    "database-testing", "ai-bug-triage", "qa-project-bootstrap", "cypress-automation",
}
# Field labels of a test case (artifact contract). Changing one means changing the
# contract, test-case-management, and tools/check_artifacts.py together.
CASE_FIELDS_EN = ["Traces", "Technique", "Level", "Priority", "Preconditions",
                  "Test data", "Steps", "Expected result"]


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    checks: int = 0

    def check(self, ok: bool, message: str) -> None:
        self.checks += 1
        if not ok:
            self.errors.append(message)


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None, text
    return (data if isinstance(data, dict) else None), text[end + 4:]


def fenced_blocks_balanced(text: str) -> bool:
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("```")) % 2 == 0


def related_names(body: str) -> list[str]:
    """Skill names listed as bullets under '## Related Skills'."""
    m = re.search(r"^## Related Skills\s*$(.*?)(?=^## |\Z)", body, re.M | re.S)
    if not m:
        return []
    return re.findall(r"^\s*-\s+\*\*([a-z0-9-]+)\*\*", m.group(1), re.M)


def description_related(desc: str) -> list[str]:
    m = re.search(r"Related:\s*(.+)$", desc, re.S)
    if not m:
        return []
    return [n.strip(" .`") for n in m.group(1).replace("\n", " ").split(",") if n.strip(" .`")]


def validate(root: Path) -> Report:
    r = Report()

    # --- manifest -------------------------------------------------------------------
    manifest_path = root / ".claude-plugin" / "plugin.json"
    r.check(manifest_path.exists(), "missing .claude-plugin/plugin.json")
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
        except json.JSONDecodeError as e:
            r.check(False, f"plugin.json is not valid JSON: {e}")
    for key in ("name", "version", "description", "license"):
        r.check(bool(manifest.get(key)), f"plugin.json: missing '{key}'")
    r.check(KEBAB.match(manifest.get("name", "")) is not None, "plugin.json: name must be kebab-case")
    r.check(SEMVER.match(manifest.get("version", "")) is not None, "plugin.json: version must be semver X.Y.Z")

    market_path = root / ".claude-plugin" / "marketplace.json"
    if market_path.exists():
        try:
            market = json.loads(market_path.read_text())
            names = [p.get("name") for p in market.get("plugins", [])]
            r.check(manifest.get("name") in names, "marketplace.json does not list this plugin by name")
        except json.JSONDecodeError as e:
            r.check(False, f"marketplace.json is not valid JSON: {e}")

    # --- skills ---------------------------------------------------------------------
    skills_dir = root / "skills"
    skill_names = sorted(p.name for p in skills_dir.iterdir() if p.is_dir())
    skill_set = set(skill_names)
    agent_names = sorted(p.stem for p in (root / "agents").glob("*.md"))
    known_names = skill_set | set(agent_names)
    adapted: dict[str, str] = {}

    for name in skill_names:
        sdir = skills_dir / name
        md = sdir / "SKILL.md"
        r.check(md.exists(), f"skills/{name}: missing SKILL.md")
        if not md.exists():
            continue
        text = md.read_text()
        fm, body = split_frontmatter(text)
        r.check(fm is not None, f"skills/{name}/SKILL.md: missing or invalid YAML frontmatter")
        if fm is None:
            continue
        r.check(fm.get("name") == name, f"skills/{name}: frontmatter name '{fm.get('name')}' != directory name")
        r.check(KEBAB.match(name) is not None and len(name) <= 64, f"skills/{name}: name must be kebab-case, <= 64 chars")
        desc = fm.get("description") or ""
        r.check(bool(desc.strip()), f"skills/{name}: empty description")
        r.check(len(desc) <= 1024, f"skills/{name}: description is {len(desc)} chars (limit 1024)")
        r.check("Use when" in desc, f"skills/{name}: description lacks a 'Use when' trigger clause")
        meta = fm.get("metadata") or {}
        r.check(meta.get("author") == "qa-agentic-pipeline",
                f"skills/{name}: metadata.author should be 'qa-agentic-pipeline' (got {meta.get('author')!r})")
        if meta.get("adapted_from"):
            adapted[name] = meta["adapted_from"]
        r.check(fenced_blocks_balanced(text), f"skills/{name}/SKILL.md: unbalanced ``` code fences")

        for rel in description_related(desc) + related_names(body):
            r.check(rel in known_names, f"skills/{name}: related skill '{rel}' does not exist in this plugin")
        for dangling in sorted(UPSTREAM_ONLY_SKILLS):
            pattern = rf"(`{dangling}`|\*\*{dangling}\*\*|\buse {dangling}\b|Related:[^\n]*\b{dangling}\b)"
            r.check(re.search(pattern, text) is None,
                    f"skills/{name}: references '{dangling}', which this plugin does not ship")
        for ref in sorted(set(re.findall(r"`references/([A-Za-z0-9_.-]+\.md)`", text))):
            r.check((sdir / "references" / ref).exists(), f"skills/{name}: mentions references/{ref}, which does not exist")
        for ref in sorted(set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", text))):
            r.check((root / ref).exists(), f"skills/{name}: points at ${{CLAUDE_PLUGIN_ROOT}}/{ref}, which does not exist")
        for ref_file in (sdir / "references").glob("*.md") if (sdir / "references").exists() else []:
            rt = ref_file.read_text()
            r.check(fenced_blocks_balanced(rt), f"skills/{name}/references/{ref_file.name}: unbalanced code fences")
            for dangling in sorted(UPSTREAM_ONLY_SKILLS):
                r.check(re.search(rf"`{dangling}`", rt) is None,
                        f"skills/{name}/references/{ref_file.name}: references '{dangling}'")

    # --- agents ---------------------------------------------------------------------
    for agent in agent_names:
        path = root / "agents" / f"{agent}.md"
        fm, body = split_frontmatter(path.read_text())
        r.check(fm is not None, f"agents/{agent}.md: missing or invalid frontmatter")
        if fm is None:
            continue
        r.check(fm.get("name") == agent, f"agents/{agent}.md: name '{fm.get('name')}' != file name")
        r.check(bool(fm.get("description")), f"agents/{agent}.md: empty description")
        r.check("<example>" in (fm.get("description") or ""), f"agents/{agent}.md: description has no <example> blocks")
        tools = fm.get("tools") or []
        for t in tools:
            r.check(t in KNOWN_TOOLS, f"agents/{agent}.md: unknown tool '{t}'")
        for sk in fm.get("skills") or []:
            r.check(sk in skill_set, f"agents/{agent}.md: preloads skill '{sk}', which does not exist")
        for sk in set(re.findall(r"`([a-z]+(?:-[a-z0-9]+)+)`", body)):
            if sk in UPSTREAM_ONLY_SKILLS:
                r.check(False, f"agents/{agent}.md: references '{sk}', which this plugin does not ship")
        r.check("artifact-contract.md" in body, f"agents/{agent}.md: does not point at the artifact contract")
        for ref in sorted(set(re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)", body))):
            r.check((root / ref).exists(), f"agents/{agent}.md: points at ${{CLAUDE_PLUGIN_ROOT}}/{ref}, which does not exist")
        r.check("qa-output-standards" in body, f"agents/{agent}.md: does not apply qa-output-standards")

    # --- orchestrator wiring --------------------------------------------------------
    orch_path = skills_dir / "run-qa-pipeline" / "SKILL.md"
    orch = orch_path.read_text() if orch_path.exists() else ""
    for agent in agent_names:
        r.check(f"`{agent}`" in orch, f"run-qa-pipeline does not orchestrate agent '{agent}'")
    stage_rows = re.findall(r"^\| \d \| `([a-z-]+)` \| (.+?) \|", orch, re.M)
    r.check(len(stage_rows) == 4, f"run-qa-pipeline: expected 4 stage rows, found {len(stage_rows)}")
    for agent, skills_cell in stage_rows:
        r.check(agent in agent_names, f"run-qa-pipeline stage table names unknown agent '{agent}'")
        for sk in re.findall(r"`([a-z0-9-]+)`", skills_cell):
            r.check(sk in skill_set, f"run-qa-pipeline stage table names unknown skill '{sk}'")

    # --- artifact contract drift ----------------------------------------------------
    contract_path = skills_dir / "run-qa-pipeline" / "references" / "artifact-contract.md"
    r.check(contract_path.exists(), "missing skills/run-qa-pipeline/references/artifact-contract.md")
    contract = contract_path.read_text() if contract_path.exists() else ""
    tcm_path = skills_dir / "test-case-management" / "SKILL.md"
    tcm = tcm_path.read_text() if tcm_path.exists() else ""
    for label in CASE_FIELDS_EN:
        r.check(f"| {label} |" in contract, f"artifact contract: field label table lacks '{label}'")
        r.check(f"**{label}**" in tcm, f"test-case-management: pipeline format lacks field '{label}'")
    for prefix in ("REQ-<n>", "Q<n>", "A<n>", "TC-<LVL>-<nnn>", "R-<n>"):
        r.check(prefix in contract, f"artifact contract: ID '{prefix}' not defined")

    # --- attribution ----------------------------------------------------------------
    notices = (root / "THIRD_PARTY_NOTICES.md").read_text() if (root / "THIRD_PARTY_NOTICES.md").exists() else ""
    r.check(bool(notices), "missing THIRD_PARTY_NOTICES.md")
    r.check("MIT License" in notices and "Petr Kindlmann" in notices,
            "THIRD_PARTY_NOTICES.md must keep the upstream MIT notice and copyright")
    for name in adapted:
        r.check(f"`{name}`" in notices, f"THIRD_PARTY_NOTICES.md does not list adapted skill '{name}'")
    for listed in re.findall(r"^\| `([a-z0-9-]+)` \|", notices, re.M):
        r.check(listed in adapted, f"THIRD_PARTY_NOTICES.md lists '{listed}' but its SKILL.md has no adapted_from")

    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=Path(__file__).resolve().parent.parent, type=Path)
    ap.add_argument("--json", action="store_true", help="print a JSON result")
    args = ap.parse_args()
    report = validate(args.root.resolve())
    if args.json:
        print(json.dumps({"checks": report.checks, "errors": report.errors,
                          "passed": not report.errors}, indent=2))
    else:
        for e in report.errors:
            print(f"FAIL  {e}")
        status = "PASS" if not report.errors else "FAIL"
        print(f"{status}: {report.checks - len(report.errors)}/{report.checks} checks passed")
    return 0 if not report.errors else 1


if __name__ == "__main__":
    sys.exit(main())
