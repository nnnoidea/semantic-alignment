import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from migrate_v1 import split_row  # noqa: E402
from recordlib import canonical_json, render_user_semantics  # noqa: E402


def run_script(name, *args, check=True):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / name), *map(str, args)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"{name} failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    return result


def begin_full_audit(records, artifact_root, *args, check=True):
    return run_script(
        "audit.py",
        records,
        "begin-full",
        "--artifact-root",
        artifact_root,
        *args,
        "--confirm-user-authorized",
        check=check,
    )


def finalize_full_audit(records, artifact_root, *args, check=True):
    return run_script(
        "audit.py",
        records,
        "finalize",
        "--artifact-root",
        artifact_root,
        "--mode",
        "full",
        "--confirm-full-scope-reviewed",
        *args,
        check=check,
    )


def record_feature_coverage(records, artifact_root, semantic_id="U1"):
    return run_script(
        "audit.py",
        records,
        "record-coverage",
        "--artifact-root",
        artifact_root,
        "--semantic-id",
        semantic_id,
        "--status",
        "satisfied",
        "--assertion-type",
        "capability",
        "--counterexample-review",
        "Checked the only feature entry path; no universal constraint applies.",
        "--source",
        "user-explicit",
        "--relation",
        "implements",
        "--implementation",
        f"feature.txt covers {semantic_id}.",
        "--evidence",
        "feature.txt",
    )


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.records = self.root / "records"
        self.project.mkdir()
        (self.project / "feature.txt").write_text("enabled\n", encoding="utf-8")
        run_script("init_records.py", self.records)
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "goal",
            "--text",
            "The feature is enabled.",
            "--reason",
            "clarification",
            "--source",
            "test",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_empty_records_validate(self):
        empty_records = self.root / "empty-records"
        run_script("init_records.py", empty_records)
        run_script("validate_records.py", empty_records)

    def test_git_snapshot_is_stable_when_an_unchanged_file_is_staged(self):
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        finalize_full_audit(self.records, self.project)
        subprocess.run(["git", "-C", str(self.project), "add", "feature.txt"], check=True)
        plan = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertFalse(sum(plan["changed_paths"].values(), []))
        version = plan["snapshot"]["files"]["feature.txt"]
        self.assertTrue(version.startswith("stat:file:"), version)
        self.assertNotIn("git:", version)
        self.assertNotIn("sha256:", version)

    def test_audit_state_has_no_policy_revision(self):
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        state = json.loads((self.records / "audit-state.json").read_text(encoding="utf-8"))
        self.assertNotIn("audit_policy_revision", state["coverage"]["U1"])
        version = state["coverage"]["U1"]["evidence"][0]["version"]
        self.assertTrue(version.startswith("stat:file:"), version)

    def test_satisfied_coverage_requires_counterexample_review(self):
        rejected = run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
            check=False,
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("requires --counterexample-review", rejected.stderr)

        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "obligation",
            "--counterexample-review",
            "Checked all applicable modes, exceptions, fallbacks, and early exits.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        state = json.loads((self.records / "audit-state.json").read_text(encoding="utf-8"))
        self.assertEqual("obligation", state["coverage"]["U1"]["assertion_type"])
        self.assertIn("fallbacks", state["coverage"]["U1"]["counterexample_review"])

        state_path = self.records / "audit-state.json"
        state["coverage"]["U1"]["assertion_type"] = "capability"
        state["coverage"]["U1"]["counterexample_review"] = ""
        state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

        invalid = run_script("validate_records.py", self.records, check=False)
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("requires non-empty counterexample_review", invalid.stderr)
        plan = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertIn("missing-counterexample-review", plan["coverage"]["stale"]["U1"])

    def test_legacy_coverage_is_not_invalidated_only_by_new_audit_fields(self):
        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        finalize_full_audit(self.records, self.project)

        state_path = self.records / "audit-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        del state["coverage"]["U1"]["assertion_type"]
        del state["coverage"]["U1"]["counterexample_review"]
        state_path.write_text(json.dumps(state) + "\n", encoding="utf-8")

        plan = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertEqual(["U1"], plan["coverage"]["valid"])
        run_script("validate_records.py", self.records)

    def test_explicit_scope_can_include_gitignored_artifacts(self):
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        (self.project / ".gitignore").write_text("generated/\n", encoding="utf-8")
        generated = self.project / "generated"
        generated.mkdir()
        (generated / "output.txt").write_text("artifact\n", encoding="utf-8")
        default_plan = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertNotIn("generated/output.txt", default_plan["snapshot"]["files"])
        explicit_plan = json.loads(
            run_script(
                "audit.py",
                self.records,
                "plan",
                "--artifact-root",
                self.project,
                "--scope",
                "generated",
                "--json",
            ).stdout
        )
        self.assertIn("generated/output.txt", explicit_plan["snapshot"]["files"])

    def test_incremental_invalidation_tracks_semantics_and_evidence(self):
        initial = run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json")
        self.assertEqual("full", json.loads(initial.stdout)["recommended_mode"])

        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        finalize_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-difference",
            "--artifact-root",
            self.project,
            "--type",
            "enhanced",
            "--source",
            "agent-added",
            "--relation",
            "extends",
            "--implementation",
            "The file also contains a newline terminator.",
            "--user-semantics",
            "U1",
            "--evidence",
            "feature.txt",
            "--impact",
            "low",
        )

        unchanged = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertEqual(["U1"], unchanged["coverage"]["valid"])
        self.assertFalse(sum(unchanged["changed_paths"].values(), []))
        self.assertFalse(unchanged["stale_differences"])

        (self.project / "unrelated.txt").write_text("new behavior\n", encoding="utf-8")
        addition = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertEqual(["U1"], addition["coverage"]["valid"])
        self.assertEqual(["unrelated.txt"], addition["changed_paths"]["added"])

        (self.project / "feature.txt").write_text("disabled\n", encoding="utf-8")
        changed = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertIn("U1", changed["coverage"]["stale"])
        self.assertIn("D1", changed["stale_differences"])

        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "update",
            "--id",
            "U1",
            "--category",
            "goal",
            "--text",
            "The feature is enabled by default.",
            "--reason",
            "correction",
            "--source",
            "test",
        )
        semantic_change = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertIn("user-semantic-changed", semantic_change["coverage"]["stale"]["U1"])
        self.assertTrue(any(reason == "semantic-changed:U1" for reason in semantic_change["stale_differences"]["D1"]))

    def test_full_finalize_requires_active_full_audit_session(self):
        record_feature_coverage(self.records, self.project)

        rejected = finalize_full_audit(self.records, self.project, check=False)

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("requires an active full audit session", rejected.stderr)

    def test_begin_full_requires_user_authorization(self):
        rejected = run_script(
            "audit.py",
            self.records,
            "begin-full",
            "--artifact-root",
            self.project,
            check=False,
        )

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("requires --confirm-user-authorized", rejected.stderr)

    def test_full_audit_requires_all_current_semantics_refreshed_in_active_run(self):
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "process",
            "--text",
            "The feature is audited.",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        begin_full_audit(self.records, self.project)
        record_feature_coverage(self.records, self.project, "U1")

        rejected = finalize_full_audit(self.records, self.project, check=False)

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("missing coverage: U2", rejected.stderr)
        self.assertIn("full audit coverage not refreshed in active run: U2", rejected.stderr)

    def test_full_audit_requires_full_scope_confirmation_even_without_changes(self):
        begin_full_audit(self.records, self.project)
        record_feature_coverage(self.records, self.project)
        finalize_full_audit(self.records, self.project)

        begin_full_audit(self.records, self.project)
        record_feature_coverage(self.records, self.project)
        rejected = run_script(
            "audit.py",
            self.records,
            "finalize",
            "--artifact-root",
            self.project,
            "--mode",
            "full",
            check=False,
        )

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("full artifact scope was not confirmed", rejected.stderr)
        finalize_full_audit(self.records, self.project)

    def test_full_audit_requires_open_differences_refreshed_in_active_run(self):
        begin_full_audit(self.records, self.project)
        record_feature_coverage(self.records, self.project)
        finalize_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-difference",
            "--artifact-root",
            self.project,
            "--type",
            "added",
            "--source",
            "agent-added",
            "--relation",
            "extends",
            "--implementation",
            "The file also contains a newline terminator.",
            "--user-semantics",
            "U1",
            "--evidence",
            "feature.txt",
            "--impact",
            "low",
        )

        begin_full_audit(self.records, self.project)
        record_feature_coverage(self.records, self.project)
        rejected = finalize_full_audit(self.records, self.project, check=False)

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("open differences not reviewed in active full audit: D1", rejected.stderr)

        run_script(
            "audit.py",
            self.records,
            "record-difference",
            "--id",
            "D1",
            "--artifact-root",
            self.project,
            "--type",
            "added",
            "--source",
            "agent-added",
            "--relation",
            "extends",
            "--implementation",
            "The file also contains a newline terminator.",
            "--user-semantics",
            "U1",
            "--evidence",
            "feature.txt",
            "--impact",
            "low",
        )
        finalize_full_audit(self.records, self.project)
        state = json.loads((self.records / "audit-state.json").read_text(encoding="utf-8"))
        self.assertNotIn("active_audit", state)
        self.assertEqual(state["last_audit"]["audit_run_id"], state["coverage"]["U1"]["audit_run_id"])
        self.assertEqual(state["last_audit"]["audit_run_id"], state["differences"][0]["audit_run_id"])

    def test_related_semantics_are_a_small_incremental_audit_context(self):
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "process",
            "--text",
            "The feature is audited.",
            "--related",
            "U1",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        begin_full_audit(self.records, self.project)
        for semantic_id in ("U1", "U2"):
            run_script(
                "audit.py",
                self.records,
                "record-coverage",
                "--artifact-root",
                self.project,
                "--semantic-id",
                semantic_id,
                "--status",
                "satisfied",
                "--assertion-type",
                "capability",
                "--counterexample-review",
                "Checked the only feature entry path; no universal constraint applies.",
                "--source",
                "user-explicit",
                "--relation",
                "implements",
                "--implementation",
                f"feature.txt covers {semantic_id}.",
                "--evidence",
                "feature.txt",
            )
        finalize_full_audit(self.records, self.project)

        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "content",
            "--text",
            "An unrelated label exists.",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        unrelated = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertEqual(["U3"], unrelated["coverage"]["missing"])
        self.assertEqual(["U1", "U2"], unrelated["coverage"]["valid"])
        self.assertEqual([], unrelated["semantic_targets"][0]["related"])

        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "update",
            "--id",
            "U2",
            "--text",
            "The feature is audited after every material change.",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        related_change = json.loads(
            run_script("audit.py", self.records, "plan", "--artifact-root", self.project, "--json").stdout
        )
        self.assertIn("user-semantic-changed", related_change["coverage"]["stale"]["U2"])
        self.assertIn("related-semantics-changed", related_change["coverage"]["stale"]["U1"])
        target = next(item for item in related_change["semantic_targets"] if item["semantic_id"] == "U1")
        self.assertEqual(["U2"], target["related"])

    def test_related_semantics_are_synchronized_by_the_tool(self):
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "process",
            "--text",
            "Audit the feature.",
            "--related",
            "U1",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        rows = [json.loads(line) for line in (self.records / "semantic-ledger.jsonl").read_text().splitlines()]
        latest = {}
        for row in rows:
            latest[row["semantic_id"]] = row
        self.assertEqual(["U2"], latest["U1"]["related"])
        self.assertEqual(["U1"], latest["U2"]["related"])

        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "update",
            "--id",
            "U2",
            "--related",
            "none",
            "--reason",
            "correction",
            "--source",
            "test",
        )
        rows = [json.loads(line) for line in (self.records / "semantic-ledger.jsonl").read_text().splitlines()]
        latest = {}
        for row in rows:
            latest[row["semantic_id"]] = row
        self.assertEqual([], latest["U1"]["related"])
        self.assertEqual([], latest["U2"]["related"])

    def test_validator_rejects_an_asymmetric_current_relation(self):
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "add",
            "--category",
            "process",
            "--text",
            "Audit the feature.",
            "--reason",
            "clarification",
            "--source",
            "test",
        )
        ledger = self.records / "semantic-ledger.jsonl"
        rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        previous = rows[-1]
        rows.append(
            {
                **previous,
                "revision": 2,
                "operation": "update",
                "before": previous["text"],
                "related": ["U1"],
            }
        )
        ledger.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")
        (self.records / "user-semantics.md").write_text(
            render_user_semantics(self.records), encoding="utf-8"
        )

        result = run_script("validate_records.py", self.records, check=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("is not symmetric", result.stderr)

    def test_audit_updates_are_immediately_persisted_and_reported_as_stale(self):
        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        finalize_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-difference",
            "--artifact-root",
            self.project,
            "--type",
            "added",
            "--source",
            "agent-added",
            "--relation",
            "extends",
            "--implementation",
            "An extra behavior is present.",
            "--evidence",
            "feature.txt",
            "--impact",
            "low",
        )
        state = json.loads((self.records / "audit-state.json").read_text(encoding="utf-8"))
        report = (self.records / "alignment-report.md").read_text(encoding="utf-8")
        self.assertFalse(state["last_audit"]["current"])
        self.assertIn("An extra behavior is present.", report)
        self.assertIn("Overall: stale", report)
        run_script("validate_records.py", self.records)

    def test_concurrent_semantic_writes_keep_unique_ids(self):
        records = self.root / "concurrent-records"
        run_script("init_records.py", records)
        processes = [
            subprocess.Popen(
                [
                    sys.executable,
                    str(SCRIPTS / "record_event.py"),
                    str(records),
                    "semantic",
                    "--operation",
                    "add",
                    "--category",
                    "goal",
                    "--text",
                    f"Semantic {index}",
                    "--reason",
                    "clarification",
                    "--source",
                    "concurrency test",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for index in range(24)
        ]
        results = [process.communicate() + (process.returncode,) for process in processes]
        self.assertFalse([(stdout, stderr) for stdout, stderr, code in results if code != 0])
        rows = [
            json.loads(line)
            for line in (records / "semantic-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(24, len(rows))
        self.assertEqual(24, len({row["semantic_id"] for row in rows}))
        run_script("validate_records.py", records)

    def test_retired_non_satisfied_semantic_does_not_block_finalize(self):
        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "partial",
            "--assertion-type",
            "obligation",
            "--source",
            "user-explicit",
            "--relation",
            "narrows",
            "--implementation",
            "Only part is implemented.",
            "--evidence",
            "feature.txt",
        )
        run_script(
            "audit.py",
            self.records,
            "record-difference",
            "--artifact-root",
            self.project,
            "--type",
            "narrowed",
            "--source",
            "agent-added",
            "--relation",
            "narrows",
            "--implementation",
            "Only part is implemented.",
            "--user-semantics",
            "U1",
            "--evidence",
            "feature.txt",
            "--impact",
            "medium",
        )
        finalize_full_audit(self.records, self.project)
        run_script("audit.py", self.records, "resolve-difference", "--id", "D1", "--status", "resolved")
        run_script(
            "record_event.py",
            self.records,
            "semantic",
            "--operation",
            "delete",
            "--id",
            "U1",
            "--reason",
            "deletion",
            "--source",
            "test",
        )
        run_script("audit.py", self.records, "finalize", "--artifact-root", self.project, "--mode", "incremental")

    def test_validator_rejects_a_second_add_revision(self):
        common = {
            "date": "2026-01-01",
            "category": "goal",
            "related": [],
            "reason": "clarification",
            "source": "test",
            "recorded_at": "2026-01-01T00:00:00Z",
        }
        rows = [
            {"semantic_id": "U1", "revision": 1, "operation": "add", "before": None, "text": "one", **common},
            {"semantic_id": "U1", "revision": 2, "operation": "add", "before": None, "text": "two", **common},
        ]
        (self.records / "semantic-ledger.jsonl").write_text(
            "".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8"
        )
        (self.records / "user-semantics.md").write_text(render_user_semantics(self.records), encoding="utf-8")
        result = run_script("validate_records.py", self.records, check=False)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("second add", result.stderr)

    def test_compromise_is_separate_and_reported(self):
        run_script(
            "record_event.py",
            self.records,
            "compromise",
            "--operation",
            "add",
            "--original-target",
            "Direct export",
            "--actual-choice",
            "Clipboard copy",
            "--gap",
            "Manual save remains",
            "--reason",
            "No file permission",
            "--evidence",
            "Permission denial",
            "--scope",
            "export",
            "--affected-user-semantics",
            "U1",
            "--recheck-condition",
            "File permission becomes available",
            "--recheck-method",
            "Attempt bounded file creation",
        )
        report = (self.records / "alignment-report.md").read_text(encoding="utf-8")
        self.assertIn("Active compromises retained internally: 1", report)
        self.assertIn('"compromise_id":"C1"', (self.records / "compromises.jsonl").read_text(encoding="utf-8"))
        begin_full_audit(self.records, self.project)
        run_script(
            "audit.py",
            self.records,
            "record-coverage",
            "--artifact-root",
            self.project,
            "--semantic-id",
            "U1",
            "--status",
            "satisfied",
            "--assertion-type",
            "capability",
            "--counterexample-review",
            "Checked the only feature entry path; no universal constraint applies.",
            "--source",
            "user-explicit",
            "--relation",
            "implements",
            "--implementation",
            "feature.txt enables the feature.",
            "--evidence",
            "feature.txt",
        )
        finalize_full_audit(self.records, self.project, "--relevant-compromise", "C1")
        report = (self.records / "alignment-report.md").read_text(encoding="utf-8")
        self.assertIn("C1", report)
        self.assertIn("Manual save remains", report)
        run_script("validate_records.py", self.records)

    def test_compromise_update_rejects_empty_required_field_without_appending(self):
        run_script(
            "record_event.py",
            self.records,
            "compromise",
            "--operation",
            "add",
            "--original-target",
            "Direct export",
            "--actual-choice",
            "Clipboard copy",
            "--gap",
            "Manual save remains",
            "--reason",
            "No file permission",
            "--evidence",
            "Permission denial",
            "--scope",
            "export",
            "--affected-user-semantics",
            "U1",
            "--recheck-condition",
            "File permission becomes available",
            "--recheck-method",
            "Attempt bounded file creation",
        )
        before = (self.records / "compromises.jsonl").read_text(encoding="utf-8")

        rejected = run_script(
            "record_event.py",
            self.records,
            "compromise",
            "--operation",
            "update",
            "--id",
            "C1",
            "--gap",
            "",
            check=False,
        )

        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("missing required compromise fields: gap", rejected.stderr)
        self.assertEqual(before, (self.records / "compromises.jsonl").read_text(encoding="utf-8"))
        run_script("validate_records.py", self.records)


class MigrationTest(unittest.TestCase):
    @staticmethod
    def write_legacy(records, rows):
        records.mkdir(parents=True)
        header = (
            "# User Semantic Ledger\n\n"
            "| ID | Date | Operation | Category | Before | After | Reason | Source | Current? | Recheck trigger |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        )
        (records / "user-semantic-ledger.md").write_text(
            header + "".join("| " + " | ".join(row) + " |\n" for row in rows),
            encoding="utf-8",
        )
        for name in (
            "user-semantics.md",
            "index.md",
            "recheck-triggers.md",
            "realization-semantics.md",
            "artifact-checks.md",
            "audits.md",
        ):
            (records / name).write_text(f"legacy {name}\n", encoding="utf-8")

    def test_v1_migration_preserves_current_semantics_and_archives_old_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = Path(temporary) / "records"
            records.mkdir()
            (records / "user-semantic-ledger.md").write_text(
                "# User Semantic Ledger\n\n"
                "| ID | Date | Operation | Category | Before | After | Reason | Source | Current? | Recheck trigger |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| U1 | 2026-09-04 | add | goal | none | Preserve intent | clarification | user | yes | Tool becomes available |\n",
                encoding="utf-8",
            )
            for name in ("user-semantics.md", "index.md", "recheck-triggers.md", "realization-semantics.md", "artifact-checks.md", "audits.md"):
                (records / name).write_text(f"legacy {name}\n", encoding="utf-8")

            preview = run_script("migrate_v1.py", records)
            self.assertIn("dry run", preview.stdout)
            run_script("migrate_v1.py", records, "--apply")
            self.assertTrue((records / "semantic-ledger.jsonl").exists())
            self.assertTrue((records / "compromises.jsonl").exists())
            self.assertTrue(any((records / "archive").glob("legacy-v1-*")))
            run_script("validate_records.py", records)

    def test_v1_migration_refuses_an_unrecognized_ledger_header(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = Path(temporary) / "records"
            records.mkdir()
            ledger = records / "user-semantic-ledger.md"
            ledger.write_text(
                "# User Semantic Ledger\n\n"
                "| ID | Date | Operation | Category | Before | After | Reason | Source | Current? | Wrong header |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| U1 | 2026-09-04 | add | goal | none | Preserve intent | clarification | user | yes | none |\n",
                encoding="utf-8",
            )
            result = run_script("migrate_v1.py", records, "--apply", check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertTrue(ledger.exists())
            self.assertFalse((records / "semantic-ledger.jsonl").exists())

    def test_v1_migration_normalizes_nonstandard_semantic_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            records = Path(temporary) / "records"
            self.write_legacy(
                records,
                [
                    [
                        "US-001",
                        "2026-09-04",
                        "add",
                        "goal",
                        "none",
                        "Preserve intent",
                        "clarification",
                        "user",
                        "yes",
                        "none",
                    ]
                ],
            )
            run_script("migrate_v1.py", records, "--apply")
            semantics = [
                json.loads(line)
                for line in (records / "semantic-ledger.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual("U1", semantics[0]["semantic_id"])
            run_script("validate_records.py", records)

    def test_v1_records_can_merge_into_one_project_and_archive_the_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "project" / ".semantic-alignment"
            source_one = root / "legacy-one"
            source_two = target / "legacy-two"
            run_script("init_records.py", target)
            self.write_legacy(
                source_one,
                [
                    [
                        "U1",
                        "2026-09-04",
                        "add",
                        "goal",
                        "none",
                        "First semantic",
                        "clarification",
                        "user",
                        "yes",
                        "Tool becomes available",
                    ]
                ],
            )
            self.write_legacy(
                source_two,
                [
                    [
                        "US-001",
                        "2026-09-05",
                        "add",
                        "system",
                        "none",
                        "Second semantic",
                        "clarification",
                        "user",
                        "yes",
                        "none",
                    ]
                ],
            )

            run_script(
                "migrate_v1.py",
                source_one,
                "--into",
                target,
                "--source-label",
                "one",
                "--apply",
            )
            run_script(
                "migrate_v1.py",
                source_two,
                "--into",
                target,
                "--source-label",
                "two",
                "--apply",
            )

            self.assertFalse(source_one.exists())
            self.assertFalse(source_two.exists())
            semantics = [
                json.loads(line)
                for line in (target / "semantic-ledger.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(["U1", "U2"], [item["semantic_id"] for item in semantics])
            compromises = [
                json.loads(line)
                for line in (target / "compromises.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(["U1"], compromises[0]["affected_user_semantics"])
            self.assertEqual(2, len(list((target / "archive").glob("legacy-v1-*"))))
            run_script("validate_records.py", target)

    def test_archive_only_does_not_import_superseded_semantics(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "project" / ".semantic-alignment"
            source = root / "legacy-pointer"
            run_script("init_records.py", target)
            self.write_legacy(
                source,
                [
                    [
                        "U1",
                        "2026-09-04",
                        "add",
                        "goal",
                        "none",
                        "Superseded pointer",
                        "clarification",
                        "user",
                        "yes",
                        "none",
                    ]
                ],
            )
            run_script(
                "migrate_v1.py",
                source,
                "--into",
                target,
                "--source-label",
                "pointer",
                "--archive-only",
                "--apply",
            )
            self.assertFalse(source.exists())
            self.assertEqual("", (target / "semantic-ledger.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(1, len(list((target / "archive").glob("legacy-v1-pointer-*"))))

    def test_legacy_table_parser_preserves_unescaped_backslashes(self):
        self.assertEqual(["U1", r"C:\tmp\file"], split_row(r"| U1 | C:\tmp\file |"))

    def test_git_submodule_changes_are_included_in_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            child = root / "child"
            parent = root / "parent"
            child.mkdir()
            parent.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=child, check=True)
            (child / "payload.txt").write_text("v1\n", encoding="utf-8")
            subprocess.run(["git", "add", "payload.txt"], cwd=child, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "initial"],
                cwd=child,
                check=True,
            )
            subprocess.run(["git", "init", "-q"], cwd=parent, check=True)
            subprocess.run(
                ["git", "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(child), "vendor/child"],
                cwd=parent,
                check=True,
            )
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qam", "submodule"],
                cwd=parent,
                check=True,
            )
            records = root / "records"
            run_script("init_records.py", records)
            before = json.loads(
                run_script("audit.py", records, "plan", "--artifact-root", parent, "--json").stdout
            )["snapshot"]
            self.assertIn("vendor/child/payload.txt", before["files"])
            (parent / "vendor/child/payload.txt").write_text("v2\n", encoding="utf-8")
            after = json.loads(
                run_script("audit.py", records, "plan", "--artifact-root", parent, "--json").stdout
            )["snapshot"]
            self.assertNotEqual(
                before["files"]["vendor/child/payload.txt"],
                after["files"]["vendor/child/payload.txt"],
            )


class WorkspaceIndexTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        self.project = self.workspace / "alpha-project"
        self.project.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def init_project(self, project=None, project_id="alpha-project", check=True):
        return run_script(
            "workspace.py",
            "init",
            project or self.project,
            "--workspace-root",
            self.workspace,
            "--project-id",
            project_id,
            check=check,
        )

    def test_init_creates_project_local_records_and_routing_only_index(self):
        self.init_project()

        records = self.project / ".semantic-alignment"
        self.assertTrue((records / "project.json").exists())
        self.assertTrue((records / "semantic-ledger.jsonl").exists())
        self.assertTrue((records / "audit-state.json").exists())

        index = json.loads(
            (self.workspace / ".semantic-alignment/projects.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {
                "schema_version": 1,
                "projects": [
                    {
                        "project_id": "alpha-project",
                        "root": "alpha-project",
                        "record_dir": "alpha-project/.semantic-alignment",
                    }
                ],
            },
            index,
        )
        self.assertNotIn("semantics", index["projects"][0])
        self.assertNotIn("audit", index["projects"][0])

        listed = json.loads(
            run_script(
                "workspace.py",
                "list",
                "--workspace-root",
                self.workspace,
                "--json",
            ).stdout
        )
        self.assertEqual(index["projects"], listed)

        artifact = self.project / "src" / "feature.py"
        artifact.parent.mkdir()
        artifact.write_text("enabled = True\n", encoding="utf-8")
        resolved = run_script(
            "workspace.py",
            "resolve",
            artifact,
            "--workspace-root",
            self.workspace,
        )
        self.assertEqual(str(records), resolved.stdout.strip())
        run_script("workspace.py", "check", "--workspace-root", self.workspace)

    def test_init_supports_workspace_root_as_project_root_without_self_deadlock(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "workspace.py"),
                "init",
                str(self.workspace),
                "--workspace-root",
                str(self.workspace),
                "--project-id",
                "workspace-project",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
        self.assertEqual(0, result.returncode, result.stderr)

        records = self.workspace / ".semantic-alignment"
        index = json.loads((records / "projects.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "project_id": "workspace-project",
                "root": ".",
                "record_dir": ".semantic-alignment",
            },
            index["projects"][0],
        )
        self.assertTrue((records / "project.json").exists())
        run_script("workspace.py", "check", "--workspace-root", self.workspace)

    def test_resolve_interprets_relative_paths_from_the_callers_working_directory(self):
        self.init_project()
        artifact = self.project / "feature.py"
        artifact.write_text("enabled = True\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "workspace.py"),
                "resolve",
                "feature.py",
                "--workspace-root",
                self.workspace,
            ],
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(str(self.project / ".semantic-alignment"), result.stdout.strip())

    def test_duplicate_ids_and_overlapping_project_roots_are_rejected(self):
        self.init_project()

        second = self.workspace / "second"
        second.mkdir()
        duplicate_id = self.init_project(second, project_id="alpha-project", check=False)
        self.assertNotEqual(0, duplicate_id.returncode)
        self.assertIn("already registered", duplicate_id.stderr)

        nested = self.project / "nested"
        nested.mkdir()
        overlap = self.init_project(nested, project_id="nested", check=False)
        self.assertNotEqual(0, overlap.returncode)
        self.assertIn("overlapping active project roots", overlap.stderr)
        self.assertFalse((nested / ".semantic-alignment").exists())

    def test_rebuild_index_uses_project_local_manifests(self):
        self.init_project()
        index_path = self.workspace / ".semantic-alignment/projects.json"
        index_path.unlink()

        run_script("workspace.py", "rebuild-index", "--workspace-root", self.workspace)
        rebuilt = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertEqual("alpha-project", rebuilt["projects"][0]["project_id"])
        run_script("workspace.py", "check", "--workspace-root", self.workspace)

    def test_check_reports_unindexed_project_records(self):
        self.init_project()
        second = self.workspace / "second"
        second.mkdir()
        second_records = second / ".semantic-alignment"
        run_script("init_records.py", second_records)
        (second_records / "project.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "project_id": "second",
                    "artifact_root": ".",
                    "record_dir": ".semantic-alignment",
                }
            )
            + "\n",
            encoding="utf-8",
        )

        result = run_script(
            "workspace.py",
            "check",
            "--workspace-root",
            self.workspace,
            "--discover",
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unindexed project record", result.stdout)

    def test_archive_project_removes_index_entry_and_preserves_records(self):
        self.init_project()
        run_script(
            "workspace.py",
            "archive-project",
            "alpha-project",
            "--workspace-root",
            self.workspace,
        )
        index = json.loads(
            (self.workspace / ".semantic-alignment/projects.json").read_text(encoding="utf-8")
        )
        self.assertEqual([], index["projects"])
        self.assertFalse((self.project / ".semantic-alignment").exists())
        archived = list((self.project / ".semantic-alignment-archive").glob("alpha-project-*"))
        self.assertEqual(1, len(archived))
        self.assertTrue((archived[0] / "semantic-ledger.jsonl").exists())
        run_script("workspace.py", "check", "--workspace-root", self.workspace)


if __name__ == "__main__":
    unittest.main()
