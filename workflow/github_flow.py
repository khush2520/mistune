"""Trusted GitHub operations for intake, release, and review publication."""

import argparse
import base64
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

from common import ApiError, SHA, SOURCE, TEST, Stop, dump, git, github, load, markdown, output


def authorize(directory):
    if os.environ["AUTOSE_FORK"] != os.environ["GITHUB_REPOSITORY"]:
        raise Stop("Set AUTOSE_FORK to the full name of the assignment fork.")
    event = load(Path(os.environ["GITHUB_EVENT_PATH"]))
    event_name = os.environ["GITHUB_EVENT_NAME"]
    manual_issue = os.environ.get("AUTOSE_DISPATCH_ISSUE", "")
    if manual_issue:
        if event_name != "workflow_dispatch" or not re.fullmatch(r"[1-9][0-9]{0,7}", manual_issue):
            raise Stop("Manual dispatch needs a valid GitHub issue number.")
    elif not ((event_name == "issues" and event.get("label", {}).get("name") == "autose")
              or (event_name == "issue_comment" and event.get("comment", {}).get("body") == "/autose")):
        raise Stop("Use the autose label or the exact /autose comment.")
    repo = github("")
    parent = repo.get("parent") or {}
    if not repo.get("fork") or parent.get("full_name") != "lepture/mistune" or repo["default_branch"] != "main":
        raise Stop("AutoSE requires a Mistune fork with main as its default branch.")
    actor = os.environ["GITHUB_TRIGGERING_ACTOR"]
    for login in {event["sender"]["login"], actor}:
        membership = github(f"/collaborators/{quote(login, safe='')}/permission")
        if membership["permission"] not in {"write", "maintain", "admin"}:
            raise Stop("The issue sender and rerun actor need repository write access.")
    issue = github(f"/issues/{manual_issue}") if manual_issue else event["issue"]
    if issue.get("pull_request") or issue["state"] != "open":
        raise Stop("The trigger needs an open issue.")
    title = issue.get("title") or ""
    body = issue.get("body") or ""
    if len(body.encode()) > 12_000:
        raise Stop("The issue description exceeds the 12 KB intake limit.")
    dump(directory / "issue.json", {"number": issue["number"], "title": title, "body": body})
    main = github("/git/ref/heads/main")["object"]["sha"]
    control = os.environ["GITHUB_SHA"]
    base = main if manual_issue else control
    if main != base:
        raise Stop("Main moved after intake; start a new run from the issue.")
    run_id = os.environ["GITHUB_RUN_ID"]
    attempt = os.environ["GITHUB_RUN_ATTEMPT"]
    branch = f"autose/issue-{issue['number']}-{run_id}-{attempt}"
    output(base=base, control=control, branch=branch, issue=issue["number"], intake=f"intake-{attempt}")


def existing_ref(branch):
    try:
        return github(f"/git/ref/heads/{quote(branch, safe='/')}")["object"]["sha"]
    except ApiError as error:
        if error.code == 404:
            return None
        raise


def certify_diff(repo, old_head):
    lines = git(repo, "diff", "--cached", "--raw", "--no-renames", "-z", old_head)
    entries = lines.decode().rstrip("\0").split("\0")
    if not lines or len(entries) % 2:
        raise Stop("The staged candidate diff is empty or unreadable.")
    for metadata, name in zip(entries[::2], entries[1::2]):
        old_mode, new_mode, _, _, change = metadata.lstrip(":").split()
        if not (SOURCE.fullmatch(name) or TEST.fullmatch(name)):
            raise Stop("The release patch edits a file outside the allowed paths.")
        if new_mode != "100644" or old_mode not in {"100644", "000000"} or change not in {"A", "M"}:
            raise Stop("The release patch changes file types, modes, or removes files.")


def push(repo, head, branch):
    token = base64.b64encode(f"x-access-token:{os.environ['GH_TOKEN']}".encode()).decode()
    env = dict(os.environ)
    env.update({
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
        "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {token}",
        "GIT_CONFIG_KEY_1": "credential.helper",
        "GIT_CONFIG_VALUE_1": "",
    })
    remote = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}.git"
    git(repo, "push", "--no-verify", remote, f"{head}:refs/heads/{branch}", env=env)


def wait_for_ci(branch, base, head, label):
    workflow = "/actions/workflows/autose-ci.yml"
    dispatch = github(workflow + "/dispatches", {"ref": branch, "inputs": {"base": base, "label": label}})
    run = dispatch.get("workflow_run_id") if dispatch else None
    limit = time.monotonic() + 420
    query = f"?event=workflow_dispatch&head_sha={head}&branch={quote(branch, safe='')}&per_page=25"
    while time.monotonic() < limit:
        if run is None:
            items = github(workflow + "/runs" + query)["workflow_runs"]
            run = next((item["id"] for item in items if item["display_title"] == f"AutoSE CI {label}"), None)
        if run is not None:
            item = github(f"/actions/runs/{run}")
            if item["head_sha"] != head or item["head_branch"] != branch:
                raise Stop("The CI run was created for a different branch or commit.")
            if item["status"] == "completed":
                return item
        time.sleep(8)
    raise Stop("CI did not finish within seven minutes.")


def release(args):
    base, old_head = args.base, args.old_head or args.base
    branch = args.branch
    issue_num = args.number
    if not (SHA.fullmatch(base) and SHA.fullmatch(old_head)):
        raise Stop("Release needs valid base and head SHAs.")
    if not re.fullmatch(rf"autose/issue-{issue_num}-\d+-\d+", branch):
        raise Stop("The release branch did not match the authorized issue.")
    if git(args.repo, "rev-parse", "HEAD").decode().strip() != old_head:
        raise Stop("The release checkout was at a different commit.")
    if github("/git/ref/heads/main")["object"]["sha"] != base:
        raise Stop("Main changed during the run; trigger a fresh attempt.")
    if load(args.build / "build_status.json")["status"] != "passed":
        raise Stop("The build and test gates did not pass.")
    patch = args.build / "diff.patch"
    if not 0 < patch.stat().st_size <= 75_000:
        raise Stop("The release patch exceeded the size limit or was empty.")
    git(args.repo, "apply", "--index", "--whitespace=nowarn", str(patch.resolve()))
    certify_diff(args.repo, old_head)
    tree = git(args.repo, "write-tree").decode().strip()
    remote_head = existing_ref(branch)
    if remote_head and remote_head != old_head:
        commit = github(f"/git/commits/{remote_head}")
        if commit["tree"]["sha"] != tree or [p["sha"] for p in commit["parents"]] != [old_head]:
            raise Stop("The existing AutoSE branch has advanced unexpectedly.")
        head = remote_head
    else:
        if args.pr and remote_head != old_head:
            raise Stop("The first review's branch no longer exists at its expected commit.")
        env = dict(os.environ, GIT_AUTHOR_NAME="AutoSE", GIT_COMMITTER_NAME="AutoSE",
                   GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com",
                   GIT_COMMITTER_EMAIL="41898282+github-actions[bot]@users.noreply.github.com")
        head = git(args.repo, "commit-tree", tree, "-p", old_head,
                   "-m", f"AutoSE issue #{issue_num} round {args.round}", env=env).decode().strip()
        push(args.repo, head, branch)
    run_url = f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    if args.pr:
        pr = github(f"/pulls/{args.pr}")
    else:
        owner = os.environ["GITHUB_REPOSITORY"].split("/")[0]
        existing = github(f"/pulls?state=open&head={quote(f'{owner}:{branch}', safe='')}&base=main")
        pr = existing[0] if existing else github("/pulls", {
            "title": f"AutoSE · Issue #{issue_num}",
            "head": branch, "base": "main",
            "body": f"Closes #{issue_num}\n\n[AutoSE run and artifacts]({run_url})\n\nA maintainer decides whether to merge.",
        })
    pr_url = pr["html_url"]
    pr_number = pr["number"]
    markdown(args.artifacts / "pr.md", "Release",
             f"[Pull request #{pr_number}]({pr_url})\n\nCommit `{head}`. CI dispatched.")
    label = f"{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}-{args.round}"
    ci = wait_for_ci(branch, base, head, label)
    ci_url = ci["html_url"]
    if ci["conclusion"] != "success":
        raise Stop(f"CI concluded {ci['conclusion']}. [CI run]({ci_url})")
    current = github(f"/pulls/{pr_number}")
    check_pr(current, head, base, branch)
    markdown(args.artifacts / "pr.md", "Release",
             f"[Pull request #{pr_number}]({pr_url})\n\n"
             f"Commit `{head}` passed [CI]({ci_url}).")
    output(pr=pr_number, head=head, pr_url=pr_url, ci_url=ci_url)


def check_pr(pr, head, base, branch):
    if (pr["state"] != "open" or pr["head"]["sha"] != head or pr["base"]["sha"] != base
            or pr["head"]["ref"] != branch or pr["base"]["ref"] != "main"
            or pr["head"]["repo"]["full_name"] != os.environ["GITHUB_REPOSITORY"]
            or pr["base"]["repo"]["full_name"] != os.environ["GITHUB_REPOSITORY"]):
        raise Stop("The PR changed or closed after release. Review the latest head manually.")


def publish(args):
    check_pr(github(f"/pulls/{args.pr}"), args.head, args.base, args.branch)
    review = load(args.review / "review.json")
    if review["head"] != args.head or review["round"] != args.round:
        raise Stop("The review artifact came from a different commit or round.")
    text = (args.review / "review.md").read_text(encoding="utf-8")
    if review["verdict"] == "request_changes" and args.round == 2:
        text += "\nTwo review rounds used. The maintainer decides how to proceed.\n"
    marker = f"<!-- autose:{os.environ['GITHUB_RUN_ID']}:{args.round}:{args.head} -->"
    # Reuse a review when GitHub accepted it but a job was retried before saving the link.
    prior = github(f"/pulls/{args.pr}/reviews?per_page=50")
    posted = next((item for item in prior if item["user"]["login"] == "github-actions[bot]"
                   and item["body"].endswith(marker)), None)
    if posted is None:
        posted = github(f"/pulls/{args.pr}/reviews", {
            "event": "COMMENT", "body": f"{text}\n\n{marker}", "commit_id": args.head,
        })
    url = posted["html_url"]
    markdown(args.artifacts / "review.md", "Posted review", f"{text}\n\n[Review on GitHub]({url})")
    output(route=review["return_to"] if args.round == 1 else "done", review_url=url)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["authorize", "release", "publish"])
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--build", type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--old-head")
    parser.add_argument("--branch")
    parser.add_argument("--round", type=int, choices=[1, 2])
    parser.add_argument("--pr", type=int)
    parser.add_argument("--number", type=int)
    args = parser.parse_args()
    args.artifacts.mkdir(parents=True, exist_ok=True)
    try:
        if args.operation == "authorize":
            authorize(args.artifacts)
        elif args.operation == "release":
            release(args)
        else:
            publish(args)
    except (Stop, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        reason = str(error) if isinstance(error, Stop) else f"An input or tool failed ({type(error).__name__})."
        filename = {"release": "pr.md", "authorize": "intake.md", "publish": "review.md"}[args.operation]
        path = args.artifacts / filename
        if path.exists():
            with path.open("a", encoding="utf-8") as stream:
                stream.write(f"\n## Stopped\n\n{reason}\n")
        else:
            markdown(path, args.operation.title(), f"Stopped. {reason}")
        raise SystemExit(reason) from None


if __name__ == "__main__":
    main()
