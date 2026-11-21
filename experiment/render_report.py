"""Render the seven-page A3 report with matplotlib."""

import csv
import os
import textwrap
from pathlib import Path
from tempfile import gettempdir

os.environ.setdefault("MPLCONFIGDIR", str(Path(gettempdir()) / "autose-matplotlib"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
INK = "#152836"
ACCENT = "#155e64"
MUTED = "#4d626d"
BG = "#eaf3f2"


class Report:
    def __init__(self, pdf):
        self.pdf = pdf
        self.page_num = 0

    def page(self, title, subtitle):
        self.page_num += 1
        self.figure = plt.figure(figsize=(8.27, 11.69))
        self.ax = self.figure.add_axes([0, 0, 1, 1])
        self.ax.set_axis_off()
        self.ax.set(xlim=(0, 1), ylim=(0, 1))
        self.ax.text(.085, .948, "AUTOMATED SOFTWARE ENGINEERING   /   ASSIGNMENT 3",
                     fontsize=9, weight="bold", color=ACCENT)
        self.ax.text(.915, .948, "2022114006", fontsize=9, ha="right", color=MUTED)
        self.ax.text(.085, .902, title, fontsize=25, weight="bold", color=INK)
        self.ax.text(.085, .865, subtitle, fontsize=10.5, color=MUTED)
        self.ax.plot([.085, .915], [.838, .838], color="#c6d8d9", linewidth=1)
        self.ax.plot([.085, .915], [.060, .060], color="#c6d8d9", linewidth=1)
        self.ax.text(.085, .035, "AUTOSE   /   MISTUNE", fontsize=8.5, color=MUTED)
        self.ax.text(.915, .035, f"{self.page_num} / 7", fontsize=8.5, ha="right", color=MUTED)
        self.y = .81

    def heading(self, title):
        self.ax.text(.085, self.y, title, va="top", fontsize=13, weight="bold", color=ACCENT)
        self.y -= .037

    def text(self, text, width=89):
        lines = textwrap.wrap(text, width=width, break_long_words=False)
        self.ax.text(.085, self.y, "\n".join(lines), va="top", fontsize=10.25, color=INK, linespacing=1.5)
        self.y -= .019 * len(lines) + .024

    def table(self, columns, rows, widths):
        x = .085
        header_height = .034
        for label, width in zip(columns, widths):
            self.ax.add_patch(plt.Rectangle((x, self.y - header_height), width, header_height, color=ACCENT))
            self.ax.text(x + .008, self.y - .017, label, fontsize=9, va="center", weight="bold", color="white")
            x += width
        self.y -= header_height
        for i, row in enumerate(rows):
            texts = [textwrap.wrap(str(value), max(6, int(w * 124) - 2), break_long_words=False)
                     for value, w in zip(row, widths)]
            height = .014 * max(len(lines) for lines in texts) + .017
            x = .085
            for lines, width in zip(texts, widths):
                self.ax.add_patch(plt.Rectangle((x, self.y - height), width, height,
                                               color=BG if i % 2 == 0 else "#f7f9f9"))
                self.ax.text(x + .008, self.y - .009, "\n".join(lines), fontsize=8.5, va="top",
                             color=INK, linespacing=1.25)
                x += width
            self.y -= height
        self.y -= .032

    def diagram(self, steps):
        y = self.y - .012
        for i, (name, detail) in enumerate(steps):
            self.ax.add_patch(FancyBboxPatch((.13, y - .040), .74, .048, boxstyle="round,pad=0.006,rounding_size=.009",
                                             facecolor=BG, edgecolor="#c6d8d9"))
            self.ax.text(.15, y - .016, name, va="center", fontsize=10.5, weight="bold", color=ACCENT)
            self.ax.text(.43, y - .016, detail, va="center", fontsize=9.5, color=INK)
            if i < len(steps) - 1:
                self.ax.annotate("", (.50, y - .061), (.50, y - .046),
                                 arrowprops={"arrowstyle": "->", "color": ACCENT, "lw": .9})
            y -= .075
        self.y = y - .006

    def finish(self):
        assert self.y >= .067, (self.page_num, self.y)
        self.pdf.savefig(self.figure)
        plt.close(self.figure)



def hosted_results():
    with (ROOT / "results/results.csv").open(newline="") as stream:
        issues = list(csv.DictReader(stream))
    with (ROOT / "results/hosted/seeded.csv").open(newline="") as stream:
        seeded = list(csv.DictReader(stream))
    latest = {}
    for row in issues:
        latest[row["case"]] = row
    completed = [row for row in latest.values() if row["conclusion"] in {"success", "failure"}]
    stages = ("requirements", "design", "implementation", "testing", "release", "review")
    rates = []
    for stage in stages:
        reached = [row for row in completed if row[stage] in {"pass", "stop"}]
        passed = sum(row[stage] == "pass" for row in reached)
        rates.append((stage.title(), f"{passed}/{len(reached)}" if reached else "—"))
    hidden = ", ".join(f"{case} {row['hidden_passed']}/{row['hidden_total']}"
                       for case, row in sorted(latest.items()) if row["hidden_total"])
    totals = sum(int(row["tokens"]) for row in issues + seeded)
    review = next((row for row in reversed(issues) if row["review_url"]), None)
    return rates, hidden, totals, review

def render():
    rates, hidden, tokens, live_review = hosted_results()
    with PdfPages(ROOT / "report.pdf", metadata={"Title": "AutoSE 3 · Issue to reviewed pull request"}) as pdf:
        page = Report(pdf)
        page.page("From issue to reviewed PR", "Architecture view 1 · Components, operations and permission boundaries")
        page.text("The fork starts from Mistune commit f7ec702edfc1ad5579a76f881238841af266d93c. "
                  "A3 reuses the A1 requirements skill and the A2 architecture document tested against this code.")
        page.diagram([
            ("Trigger gate", "GitHub reads sender permission and snapshots the issue."),
            ("Builder", "Four stages share checked files. Model replies are JSON."),
            ("Offline checker", "A disposable container builds a wheel and runs pytest."),
            ("Release + CI", "A trusted script publishes the patch and checks its SHA."),
            ("Independent review", "A fresh review context uses the issue, diff and tree."),
            ("Review publisher", "A separate job records the verdict. A maintainer decides."),
        ])
        page.heading("Where credentials live")
        page.text("Build and review each start a loopback Qwen process. The release job has Contents, Pull requests, and Actions write permissions. "
                  "The review job has Contents read. Its publisher can post a review. Generated code runs in an offline container with a product-only source tree.")
        page.finish()

        page.page("What runs, in order", "Architecture views 2 and 3 · F1 sequence and artifact hand-offs")
        if live_review:
            page.heading(f"Recorded hosted run · {live_review['case']}")
            page.text(f"GitHub Actions run {live_review['run_id']} took the issue through requirements, "
                      "design, implementation and testing. The release job pushed the checked patch and waited on same-head CI. "
                      f"The independent review posted its verdict on the pull request.")
        else:
            page.heading("Recorded local run · F1")
            page.text("The first wheel built but the new test failed because the CLI still wrote to the dash file. "
                      "The retry fixed the condition. A fresh reviewer context requested an independent build and tests. "
                      "The view records a local scripted run while the hosted trials are tracked in the ledger.")
        page.table(["Stage", "Role", "Artifact", "Gate"], [
            ("Requirements", "A1 agent", "spec.md", "Testable criteria and no unresolved decision"),
            ("Design", "A2 designer", "design.md", "Valid paths and named symbols"),
            ("Implementation", "Implementer", "diff.patch", "Wheel builds"),
            ("Testing", "Tester", "test_report.md", "Full suite and mapped tests pass"),
            ("Release", "GitHub script", "pr.md", "Same-head CI succeeds; PR open"),
            ("Review", "Fresh reviewer", "review.md", "Approve or end after round two"),
        ], [.17, .16, .19, .31])
        page.heading("Hosted ordering")
        page.text("On GitHub the maintainer label or command starts the first round. The release job waits for a separate workflow dispatched against "
                  "the exact PR head. A publisher records review one. An approach finding can send the run back to design, and a local finding can send it back to implementation.")
        page.text("A blocked requirement produces questions. A failed build or test gets one retry per round. A second review request stays visible on the PR.")
        page.finish()

        page.page("Decisions at a glance", "The first decision records and component view were committed before the workflow.")
        page.table(["ID", "Chosen option", "Alternative", "Main reason", "State"], [
            ("001", "Four roles + script", "One agent for all", "Independent review and deterministic release", "Used"),
            ("002", "Two explicit rounds", "Model router", "Bounded, inspectable feedback loops", "Used"),
            ("003", "Checked artifacts", "Full transcripts", "Preserve traceability and reviewer independence", "Used"),
            ("004", "Actions artifacts", "Commit every log", "Keep experiment state off the product branch", "Used"),
            ("005", "Fixed operations", "General shell/MCP", "Scope execution and GitHub writes", "Used"),
            ("006", "GPT-4.1 mini", "Different models", "Stable role comparison", "Replaced"),
            ("007", "Executed criteria", "Test names only", "A collected case can fail or skip", "Used"),
            ("008", "Fresh review job", "Shared model context", "Review the patch on its own evidence", "Used"),
            ("009", "Bounded offline runner", "Prompt controls only", "Restrict what generated code can do", "Used"),
            ("010", "Write check + queue", "Author association", "Check real repo permission", "Used"),
            ("011", "GPT-5.4 mini API", "Deprecated snapshot", "Use a pinned API model", "Replaced"),
            ("012", "Qwen on public CPU", "Remote model API", "Set provider inference spend to $0", "Used"),
            ("013", "Compact A1 intake", "Full A1 prompt", "Avoid questions already answered by the issue", "Used"),
        ], [.062, .209, .175, .288, .096])
        page.text("ADR 012 replaces the paid API option. ADR 013 records the intake change after the first hosted attempts.")
        page.finish()

        page.page("Three decisions that mattered", "How prior work informed the design")
        page.heading("D3 · Carry evidence forward in files")
        page.text("A1 separates confirmed evidence from assumptions and requires observable acceptance criteria. That is useful in an issue queue because the maintainer "
                  "may be offline by the time a run begins. Spec.md holds the A1 outputs for the run. Open questions about behavior stop there, so later stages do not have to guess.")
        page.text("The designer consumes the original A2 architecture with a live index of paths and symbols. In the recorded A2 results, the cross-component T3 had "
                  "one regression in each run without the document and zero in the two runs with the full document. Both conditions had one complete T3 result. "
                  "This small comparison helps explain why the document is a design input.")
        page.heading("D7 · Require evidence of test execution")
        page.text("A passing wheel shows the project can be built. A test definition shows an acceptance case was written. The full suite and JUnit together establish "
                  "that a case ran and passed. Reviewer judgment is still needed to see whether the assertions actually check the requested behavior.")
        page.heading("D8 · Give the reviewer a separate job")
        page.text("The reviewer sees the issue, final diff and files from the checked-out commit. It can ask for an isolated rerun. "
                  "The builder's spec, design, reports and conversation stay out of the review context. Its output has to cite concrete lines when asking for changes.")
        page.text("Implementation and review use separate loopback inference processes with the same pinned Qwen weights. This keeps the model fixed. Correlated mistakes remain possible.")
        page.finish()

        page.page("Decision experiments", "Paired gate checks and a hosted reviewer comparison")
        page.table(["Probe", "Comparison", "Observed result"], [
            ("D7 · Five test cases", "Test definition only", "2/5 correct gate decisions. The skip, failure and uncollected test were accepted."),
            ("D7 · Same tests", "Definition + executed case", "5/5 correct. Only the real passing case advanced."),
            ("D8 · Five seeded diffs", "Accept raw verdict", "Accepted 5/5 scripted responses, including one incorrect approval."),
            ("D8 · Same responses", "Require consistent evidence", "Accepted 2/5 valid approvals. Stopped three malformed responses."),
        ], [.20, .22, .41])
        page.heading("D7 · The uncollected case matters")
        page.text("The full suite was green when pytest ignored the candidate test. The criterion still failed the JUnit gate because no executed case carried its ID. "
                  "This check stays in the workflow.")
        page.heading("D8 · An invalid response is a distinct outcome")
        page.text("A reply claimed approval while listing a blocking problem. A second cited a line beyond the file. A third asked for changes without a finding. "
                  "The publisher must never receive these as valid verdicts. The evidence gate stopped all three.")
        page.text("A live Qwen trial compared the full and terse reviewer prompts on the same five draft PRs. Both scored 3/5. Each caught the hardcoded filename in R5. Both missed R2 overwriting the dash file and R3 accepting empty stdin.")
        page.text("Keep the evidence gate. The five cases did not justify a model or prompt change. A focused regression check would provide more targeted evidence than a passing baseline alone.")
        page.finish()

        page.page("Results", "Latest hosted attempt per issue and the independent evaluator")
        page.table(["Stage", "Passed / reached", "Check"], [
            (stage, rate, note) for (stage, rate), note in zip(rates, [
                "Testable spec ready to hand off",
                "Paths and symbols validated",
                "Wheel built on the candidate",
                "Full suite and mapped cases passed",
                "PR open and CI green at its head",
                "Independent verdict posted",
            ])
        ], [.25, .24, .34])
        page.heading("Held-out checks")
        page.text("The pinned baseline passed 1,327 tests and 158 subtests. The local F1 candidate passed all three hidden cases. "
                  "The V1 hidden checks evaluate the requirements artifact because an ambiguous issue should stop before release.")
        page.text("Hosted hidden scores were recorded as follows. " + (hidden or "No held-out score was available when this report was generated."))
        page.heading("Hosted observations")
        if live_review:
            page.text(f"{live_review['case']} produced a tested PR with a posted {live_review['verdict'].replace('_', ' ')} verdict. "
                      "The run ledger links to the issue, CI and review.")
        else:
            page.text("The initial model repeatedly requested details already given in the issue. The compact intake cleared four concrete issues on the next attempt. Subsequent gates stopped on model or test failures. GitHub then refused new dispatches with HTTP 422, leaving release and review unverified for issue runs.")
        page.text(f"Qwen reported {tokens:,} tokens across the hosted issue and seeded-review runs. Total paid model spend was $0. "
                  "Requests that timed out without returning usage are excluded from the token count.")
        page.finish()

        page.page("Hindsight and validity", "What the evidence supports and what still needs measurement")
        page.heading("First change")
        page.text("Use a brief text-proposal turn before asking the implementer for complete file bodies. Whole-file edits make the patch easy to apply locally, "
                  "but each larger source file increases the input and output budget. A smaller verified change format could make multi-file work feasible without giving the model shell access.")
        page.heading("Limitations")
        page.text("1. One repository and four small product tasks. The current scope excludes changes to dependencies and workflow configuration, so these results do not predict performance on large changes.")
        page.text("2. The local gate experiments use scripted responses. The hosted cohort tests live model behavior on five code changes. Those results have different denominators.")
        page.text("3. The fixture author also supplied the expected labels. Seeded issues emphasize cases the author anticipated. Independent labeling would reduce this bias.")
        page.text("4. Structural checks can be satisfied by weak assertions. Test mappings and a valid line reference still need behavior-based review.")
        page.text("5. Docker verification used a local Apple Silicon machine. Hosted runner setup, token permissions and service latency can affect a live run.")
        page.heading("Reproducibility")
        page.text("The fork includes the pinned commit, workflow copy, prompts, decision variants, run ledger and raw evidence. The hidden evaluator stays outside the candidate repository.")
        page.finish()


if __name__ == "__main__":
    render()
