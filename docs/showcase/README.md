# See what the Skill actually produces

These are Semantic Alignment's own user agreements and a completed check of its implementation. Open the actual output, follow a finding into the diagram, and inspect the wording and evidence behind it.

- [Read the project's current user agreements](SEMANTICS.md).
- [Open the difference summary](https://nnnoidea.github.io/semantic-alignment/showcase/checks/2026-11-09-state-fixes/summary.html).
- [Explore the interactive diagrams](https://nnnoidea.github.io/semantic-alignment/showcase/checks/2026-11-09-state-fixes/index.html).
- [Read the editable check report](checks/2026-11-09-state-fixes/report.md) or [supporting maintenance notes](MAINTENANCE.md).

The README screenshots show the published summary and a node opened from it; that navigation and page scrolling were checked in the browser. This is not a full responsive, keyboard or printing test.

The records and report keep the original Chinese wording. The dated report includes its frozen agreement baseline; the separate records reflect later accepted changes too. This check predates the removal of Chinese review copies and the publication/download setup. Those changes have not been rechecked by this report.

After the two reported state-display issues were repaired, this snapshot lists 172 Agent-added choices and 6 verification gaps. These are reported entries, not a defect total. Zero listed violations or deviations is not proof of complete agreement. Earlier local evidence references are retained as provenance; unpublished material is not offered as a working link.

## Read online, download only when wanted

This showcase is published specifically for this project. It does not authorize the Skill to upload records from other projects.

The `export-ignore` rules omit this directory from source archives, including the ordinary GitHub ZIP download. A full Git clone still includes it. Installation only needs `SKILL.md`, `agents/`, `references/` and `assets/`; these examples are not runtime inputs or part of the installed Skill.

For an offline copy, clone the repository and open `summary.html` or `index.html` in the dated check directory, keeping both HTML files together. To rebuild that check from its editable input, run from the repository root:

```sh
python3 -B docs/showcase/checks/2026-11-09-state-fixes/report.py
```

The report uses the bundled templates. Machine-specific addresses have been replaced with repository paths; the findings and their original scope remain intact.
