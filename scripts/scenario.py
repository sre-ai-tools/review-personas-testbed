#!/usr/bin/env python3
"""Pin, run and record review-personas testbed scenarios (0002 design T4, T6, T8).

    scripts/scenario.py pin <ref> [--tool-repo PATH]    point the testbed at a review-personas version
    scripts/scenario.py run <id>... | all [--yes]      open (or reset) scenario PRs: calls Bedrock
    scripts/scenario.py local <id>                     scenario branch for /prpanel:review, not pushed
    scripts/scenario.py record <version>               write a results checklist for this run
    scripts/scenario.py clean [--pins]                 close scenario PRs and delete their branches

A scenario id is its number or folder name: `s2`, `S02`, `s02-aws-open-ssh`.
Needs Python 3.12+, git, and gh logged in with write access to both repos. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "scenarios"
WORKFLOW = Path(".github/workflows/review-personas.yml")
RESULTS = ROOT / "results"
TOOL_REVIEW_YML = ".github/workflows/review.yml"
BRANCH_PREFIX = "scenario/"
PIN_PREFIX = "testbed/"

# The caller's `uses:` line, and the "# pinned:" comment that `pin` writes above it.
CALLER_USES = re.compile(
    r"^(\s*uses: sre-ai-tools/review-personas/\.github/workflows/review\.yml)@\S+$", re.M
)
PINNED = re.compile(r"^(\s*# pinned: )(.*)$", re.M)
# The same expression release.yml uses to point review.yml's action at a release (0001 D11).
TOOL_ACTION = re.compile(r"(uses: sre-ai-tools/review-personas)@[^\s]+")
RELEASE_TAG = re.compile(r"^v\d+(\.\d+\.\d+)?$")


class ScriptError(Exception):
    pass


def sh(*args: str, cwd: Path = ROOT, input: str | None = None, env: dict | None = None) -> str:
    proc = subprocess.run(
        args, cwd=cwd, input=input, env=env, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise ScriptError(f"`{' '.join(args)}` failed:\n{proc.stderr.strip() or proc.stdout.strip()}")
    return proc.stdout.strip()


def ok(*args: str, cwd: Path = ROOT) -> bool:
    return subprocess.run(args, cwd=cwd, capture_output=True, check=False).returncode == 0


# ---------------------------------------------------------------- scenarios


@dataclass
class Scenario:
    path: Path
    title: str
    body: str
    ci_only: bool

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def label(self) -> str:
        return "S" + str(int(self.name[1:3]))

    @property
    def branch(self) -> str:
        return BRANCH_PREFIX + self.name

    @property
    def followup(self) -> Path | None:
        p = self.path / "followup.patch"
        return p if p.exists() else None


def parse_pr_yml(text: str, where: Path) -> tuple[str, str, bool]:
    """Reads the small subset of YAML pr.yml uses: `title: …`, `ci_only: true`, `body: |` block."""
    title, body_lines, ci_only, in_body = None, [], False, False
    for line in text.splitlines():
        if in_body:
            if line.startswith("  ") or not line.strip():
                body_lines.append(line[2:])
                continue
            in_body = False
        if line.startswith("title:"):
            title = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("ci_only:"):
            ci_only = line.split(":", 1)[1].strip() == "true"
        elif line.rstrip() == "body: |":
            in_body = True
        elif line.strip() and not line.startswith("#"):
            raise ScriptError(f"{where}: unexpected line {line!r}")
    if not title:
        raise ScriptError(f"{where}: missing title")
    return title, "\n".join(body_lines).strip() + "\n", ci_only


def load(path: Path) -> Scenario:
    title, body, ci_only = parse_pr_yml((path / "pr.yml").read_text(), path / "pr.yml")
    return Scenario(path, title, body, ci_only)


def all_scenarios() -> list[Scenario]:
    return [load(p) for p in sorted(SCENARIOS.iterdir()) if p.is_dir() and re.match(r"s\d\d-", p.name)]


def find(ident: str) -> Scenario:
    m = re.fullmatch(r"[sS]0*(\d+)(-.*)?", ident)
    if not m:
        raise ScriptError(f"Not a scenario id: {ident}")
    prefix = f"s{int(m.group(1)):02d}-"
    matches = [p for p in SCENARIOS.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if len(matches) != 1:
        raise ScriptError(f"No scenario {ident}")
    return load(matches[0])


# ---------------------------------------------------------------- testbed state


def require_clean_tree() -> None:
    if sh("git", "status", "--porcelain"):
        raise ScriptError("The testbed working tree has changes. Commit or stash them first.")


def pinned(workflow_text: str) -> str | None:
    m = PINNED.search(workflow_text)
    value = m.group(2).strip() if m else "none"
    return None if value == "none" else value


def sync_main() -> None:
    sh("git", "fetch", "--quiet", "origin")
    sh("git", "checkout", "--quiet", "main")
    sh("git", "merge", "--quiet", "--ff-only", "origin/main")


# ---------------------------------------------------------------- pin (T4)


def pin_branch(tool: Path, sha: str) -> str:
    """Pushes testbed/<sha7>: commit `sha` plus one commit pointing review.yml's action at `sha`."""
    review = sh("git", "show", f"{sha}:{TOOL_REVIEW_YML}", cwd=tool)
    rewritten, count = TOOL_ACTION.subn(rf"\1@{sha}", review, count=1)
    if count != 1:
        raise ScriptError(f"{TOOL_REVIEW_YML} at {sha[:7]} has no `uses: sre-ai-tools/review-personas@…` line")
    blob = sh("git", "hash-object", "-w", "--stdin", cwd=tool, input=rewritten + "\n")
    # Build the commit with a throwaway index, so the tool clone's checkout is never touched.
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        sh("git", "read-tree", sha, cwd=tool, env=env)
        sh("git", "update-index", "--cacheinfo", f"100644,{blob},{TOOL_REVIEW_YML}", cwd=tool, env=env)
        tree = sh("git", "write-tree", cwd=tool, env=env)
    commit = sh(
        "git", "commit-tree", tree, "-p", sha,
        "-m", f"Testbed pin: run the action at {sha}\n\nCreated by review-personas-testbed scripts/scenario.py.",
        cwd=tool,
    )  # fmt: skip
    branch = PIN_PREFIX + sha[:7]
    sh("git", "push", "--quiet", "--force", "origin", f"{commit}:refs/heads/{branch}", cwd=tool)
    return branch


def cmd_pin(args: argparse.Namespace) -> None:
    tool = Path(args.tool_repo).resolve()
    if not (tool / TOOL_REVIEW_YML).exists():
        raise ScriptError(f"{tool} is not a review-personas clone (use --tool-repo)")
    require_clean_tree()
    sync_main()
    sh("git", "fetch", "--quiet", "--tags", "origin", cwd=tool)

    ref = args.ref
    if RELEASE_TAG.match(ref):
        sha = sh("git", "rev-parse", "--verify", f"refs/tags/{ref}^{{commit}}", cwd=tool)
        uses_ref = ref  # The release job already pointed the action at this release.
    else:
        candidates = (ref, f"origin/{ref}")
        resolved = [c for c in candidates if ok("git", "rev-parse", "--verify", "-q", f"{c}^{{commit}}", cwd=tool)]
        if not resolved:
            raise ScriptError(f"{ref} is not a commit, branch or tag in {tool}")
        sha = sh("git", "rev-parse", f"{resolved[0]}^{{commit}}", cwd=tool)
        uses_ref = pin_branch(tool, sha)
        print(f"Pushed review-personas branch {uses_ref} (action at {sha[:7]}).")

    text = (ROOT / WORKFLOW).read_text()
    text, n_uses = CALLER_USES.subn(rf"\1@{uses_ref}", text)
    text, n_pin = PINNED.subn(rf"\g<1>{ref} ({sha[:7]})", text)
    if n_uses != 1 or n_pin != 1:
        raise ScriptError(f"{WORKFLOW} needs exactly one `# pinned:` comment and one review.yml `uses:` line")
    (ROOT / WORKFLOW).write_text(text)
    sh("git", "commit", "--quiet", "-m", f"Pin review-personas {ref} ({sha[:7]})", "--", str(WORKFLOW))
    sh("git", "push", "--quiet", "origin", "main")
    print(f"Testbed now runs review-personas {ref} ({sha[:7]}) via review.yml@{uses_ref}.")


# ---------------------------------------------------------------- run (T6)


def close_scenario_pr(branch: str) -> None:
    numbers = sh("gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number", "--jq", ".[].number")
    for number in numbers.split():
        sh("gh", "pr", "close", number, "--comment", "Reset by scenario.py.")
    if sh("git", "ls-remote", "--heads", "origin", branch):
        sh("git", "push", "--quiet", "origin", "--delete", branch)


def commit_patch(patch: Path, message: str) -> None:
    sh("git", "apply", "--index", "-", input=patch.read_text())
    sh("git", "commit", "--quiet", "-m", message)


def wait_for_review(branch: str, head_sha: str, timeout: int = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        run_id = sh(
            "gh", "run", "list", "--workflow", WORKFLOW.name, "--branch", branch, "--limit", "5",
            "--json", "databaseId,headSha", "--jq", f'map(select(.headSha == "{head_sha}"))[0].databaseId // ""',
        )  # fmt: skip
        if run_id:
            print(f"  waiting for review run {run_id}…")
            # The scenario's checklist judges the run's result, so a failed run doesn't stop us.
            subprocess.run(["gh", "run", "watch", run_id, "--interval", "10"], cwd=ROOT, capture_output=True)
            return
        time.sleep(5)
    raise ScriptError(f"No review run started for {branch} within {timeout}s. Check the caller workflow's `if:`.")


def cmd_run(args: argparse.Namespace) -> None:
    if args.ids == ["all"]:
        scenarios = all_scenarios()
    else:
        scenarios = [find(i) for i in args.ids]
    # Scenarios with a follow-up push wait for their first review, so run them last.
    scenarios.sort(key=lambda s: s.followup is not None)

    require_clean_tree()
    sync_main()
    pin = pinned(sh("git", "show", f"origin/main:{WORKFLOW}"))
    if pin is None:
        raise ScriptError("The testbed isn't pinned to a review-personas version. Run `scenario.py pin <ref>` first.")
    if len(scenarios) > 1 and not args.yes:
        answer = input(f"Open {len(scenarios)} scenario PRs on review-personas {pin}? Each one calls Bedrock. [y/N] ")
        if answer.strip().lower() != "y":
            return

    try:
        for s in scenarios:
            print(f"{s.label}: {s.title}")
            close_scenario_pr(s.branch)
            sh("git", "checkout", "--quiet", "-B", s.branch, "origin/main")
            commit_patch(s.path / "change.patch", f"{s.label}: {s.title}")
            sh("git", "push", "--quiet", "--force", "origin", s.branch)
            url = sh(
                "gh", "pr", "create", "--base", "main", "--head", s.branch,
                "--title", f"[{s.label}] {s.title}", "--body-file", "-", input=s.body,
            )  # fmt: skip
            print(f"  {url}")
            if s.followup:
                wait_for_review(s.branch, sh("git", "rev-parse", "HEAD"))
                commit_patch(s.followup, f"{s.label}: follow-up")
                sh("git", "push", "--quiet", "origin", s.branch)
                print("  pushed the follow-up commit")
    finally:
        sh("git", "checkout", "--quiet", "main")
    print(f"Check each PR against scenarios/<id>/expect.md, and fill in `scenario.py record {pin.split()[0]}`.")


# ---------------------------------------------------------------- local (T7)


def cmd_local(args: argparse.Namespace) -> None:
    s = find(args.id)
    if s.ci_only:
        raise ScriptError(f"{s.label} is CI-only (RUN-4). Use `scenario.py run {s.label.lower()}`.")
    require_clean_tree()
    sh("git", "checkout", "--quiet", "-B", s.branch, "main")
    commit_patch(s.path / "change.patch", f"{s.label}: {s.title}")
    print(
        f"On local branch {s.branch} (not pushed).\n"
        f"In Claude Code, run:  /prpanel:review --base main\n"
        f"Check it against scenarios/{s.name}/expect.md, skipping (CI) items.\n"
        f"Then confirm `git status` is clean and run `git checkout main`."
    )


# ---------------------------------------------------------------- record (T8)

TAG = re.compile(r"^\((CI|local)\)\s*", re.I)


def cmd_record(args: argparse.Namespace) -> None:
    pin = pinned((ROOT / WORKFLOW).read_text()) or "not pinned"
    today = dt.date.today().isoformat()
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", args.version)
    out = RESULTS / f"{today}-{safe}.md"
    if out.exists():
        raise ScriptError(f"{out.relative_to(ROOT)} already exists")

    lines = [
        f"# Verification: review-personas {args.version}",
        "",
        f"- **Pinned:** {pin}",
        f"- **Date:** {today}",
        "- **Started:** ",
        "- **Finished:** ",
        "- **Verified by:** ",
        "",
        "Replace each ☐ with ✅ or ❌. Add every ❌ to Failures with a link to a review-personas issue.",
    ]
    for s in all_scenarios():
        heading, items = None, []
        for line in (s.path / "expect.md").read_text().splitlines():
            if line.startswith("# "):
                heading = line[2:].strip()
            elif line.startswith("- [ ] "):
                items.append(line[6:].strip())
        lines += ["", f"## {heading or s.label}", "", "| Check | CI | Local |", "|---|---|---|"]
        for item in items:
            tag = TAG.match(item)
            text = TAG.sub("", item).replace("|", "\\|")
            ci = "N/A" if tag and tag.group(1).lower() == "local" else "☐"
            local = "N/A" if s.ci_only or (tag and tag.group(1).upper() == "CI") else "☐"
            lines.append(f"| {text} | {ci} | {local} |")
    lines += ["", "## Failures", "", "| Scenario | Check | Path | Issue |", "|---|---|---|---|", ""]

    RESULTS.mkdir(exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"Wrote {out.relative_to(ROOT)}. Fill it in, then commit it to main.")


# ---------------------------------------------------------------- clean


def cmd_clean(args: argparse.Namespace) -> None:
    for branch in sh("gh", "pr", "list", "--state", "open", "--limit", "200",
                     "--json", "headRefName", "--jq", ".[].headRefName").split():  # fmt: skip
        if branch.startswith(BRANCH_PREFIX):
            close_scenario_pr(branch)
    for line in sh("git", "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH_PREFIX}*").splitlines():
        sh("git", "push", "--quiet", "origin", "--delete", line.split("refs/heads/", 1)[1])
    current = sh("git", "branch", "--show-current")
    for branch in sh("git", "branch", "--list", f"{BRANCH_PREFIX}*", "--format=%(refname:short)").split():
        if branch != current:
            sh("git", "branch", "-D", branch)
    print("Closed scenario PRs and deleted scenario branches.")

    if args.pins:
        tool = Path(args.tool_repo).resolve()
        heads = sh("git", "ls-remote", "--heads", "origin", f"refs/heads/{PIN_PREFIX}*", cwd=tool).splitlines()
        names = [h.split("refs/heads/", 1)[1] for h in heads]
        if not names:
            return
        answer = input(f"Delete {len(names)} review-personas branches ({', '.join(names)})? [y/N] ")
        if answer.strip().lower() == "y":
            for name in names:
                sh("git", "push", "--quiet", "origin", "--delete", name, cwd=tool)
            print("Deleted pin branches.")


# ---------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    tool_default = str(ROOT.parent / "review-personas")

    p = sub.add_parser("pin", help="point the testbed at a review-personas version")
    p.add_argument("ref", help="release tag (v1.2.3, v1), branch or commit")
    p.add_argument("--tool-repo", default=tool_default, help="local review-personas clone")
    p.set_defaults(func=cmd_pin)

    p = sub.add_parser("run", help="open or reset scenario PRs (calls Bedrock)")
    p.add_argument("ids", nargs="+", help="scenario ids, or `all`")
    p.add_argument("--yes", action="store_true", help="don't ask before running several scenarios")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("local", help="create a local scenario branch for /prpanel:review")
    p.add_argument("id")
    p.set_defaults(func=cmd_local)

    p = sub.add_parser("record", help="write a results checklist")
    p.add_argument("version", help="the review-personas version being verified")
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("clean", help="close scenario PRs and delete scenario branches")
    p.add_argument("--pins", action="store_true", help="also delete testbed/* branches in review-personas")
    p.add_argument("--tool-repo", default=tool_default, help="local review-personas clone")
    p.set_defaults(func=cmd_clean)

    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ScriptError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
