# Check Report Template Usage

Supply semantic-check [findings and sources](view-content.md) to the bundled report templates; they provide SVG drawing, layout, styling, legends and interaction.

## Generate

Define `REPORT` in a trusted local Python file, using [layers-example.py](../assets/audit-svg/layers-example.py) as a complete fictional input example.

```sh
python3 -B <skill>/assets/audit-svg/flow.py <trusted-report.py> <report-directory>
python3 -B <skill>/assets/audit-svg/flow.py --check <report-directory>/index.html
```

Generation includes checks; `--check` rechecks an existing report. A Python builder may import `build_report(REPORT, out)` from the located asset package; the CLI executes the supplied Python file.

## Fill The Report

| Input | Fields |
| --- | --- |
| `REPORT` | `root` view key, `data`, `views` mapping; optional HTML `summary`. |
| `data` | `title`, `scope`, `date`; optional `project`, HTML `source_html`, `perspective='realization'`. |
| View | `title`, `layout`, `nodes` mapping, explicit `edges` list; optional `groups`, context `fields`, `level_label`; child views need boundary mappings below. |
| Node | `label` following the [wording rules](view-content.md#evidence), detail/state fields; optional `child` view key and `shape`: `box` (operation), `decision`, `doc` (information), `terminal` (entry/result). |
| Edge | `from`, `to`, `label`, detail/state fields; `kind`: `flow`, `data` (exchange/call/return), `error`, `constraint` (association), or general `relation`; optional `conditional`. |
| Group | `key`, `label`, `members`, detail/state fields. |

Project keys are `goal`, `scope`, `constraints`, `acceptance`; context field keys are `purpose`, `inputs`, `outputs`, `behavior`, `boundaries`, `acceptance`, each accepting a source cell below.

Map the Markdown record into report input without changing its meaning:

| Record content | Report destination |
| --- | --- |
| Purpose and constraints | Project/topic context fields. |
| Final expectation and current-stage agreement | Both in `specified`, with stage labels and complete source context; `choice` comes only from independently checked artifacts. |
| Stage completion criteria | `acceptance`; unstated criteria remain unspecified. |
| Related agreements | Evidenced graph relationships. |
| Related files | Source context/navigation; paths alone are not implementation evidence. |

Use simple view keys without `--`, local node keys and `#view--node` for cross-view links; link only useful existing targets, and escape quoted material in authored HTML fields.

## Choose A Layout And Expansion

| `layout.kind` | Input |
| --- | --- |
| `sequence` | `order: [node, ...]` |
| `branch` | `decision`, `branches: [[node, ...], ...]`, `merge`; at least two branches and one work path; an empty path is a bypass. |
| `wait` | `main`, `worker`, optional `worker_start` column. |
| `interaction` | `lanes: [[node, ...], ...]`; `None` reserves alignment space. |

Place each node once and provide edges explicitly; placement does not infer relationships.

Use `child` for **user agreement → actual flow → optional key steps**, at most three diagram levels. Keep each local graph simple, usually 4–7 principal nodes, with relevant conditions/failures visible and all detail reachable. `level_label` overrides a view’s default heading when a requested architecture overview or non-executing rule needs different wording.

Each child has one parent owner; cover both input and output with `handoffs` or corresponding `input_gap`/`output_gap` explanations:

| Handoff field | Meaning |
| --- | --- |
| `direction`, `inner` | `in`/`out` and the internal node key. |
| `outer` | A parent-local node key or `(ancestor_view, node)`. |
| `label`, `condition` | Input/result/effect and its branch or completion condition. |
| `kind` | `flow`, `data` (default), `error`, or `constraint`. |
| Detail/state fields | Relationship meaning and evidence, as for nodes and edges. |

The template generates the whole-parent frame and upper-context references; supply actual entry and continuation mappings with matching contracts, keeping returns, asynchronous effects and completion distinct. A self-completion exit may point to its parent as **本步骤完成**.

## Supply Details And State

Nodes, edges, groups and handoffs share `purpose` (one specific sentence), `specified` (用户要求), `choice` (实际做法) and `impact` (影响与取舍); keep overall check conclusions and repair questions in the full report while presenting concrete findings directly.

For precise navigation, add `links=[{"target":"view--node","label":"View shared implementation"}]`. A target is a local item key, qualified `view--node`, or full-report anchor, without `#`. Item targets automatically gain return links to the referring items; report anchors do not. Keep one child owner for shared flows and use these links from other agreements.

A source cell is text or `{text, origin, source, context, missing}`; preserve full wording, conditions, values and provenance, marking unknown behavior **未核实** and unavailable purpose/effects explicitly.

For text-level comparison, add `comparisons=[{kind, title, specified?, choice?, note, impact?}]` to a node, edge, group or handoff. `kind` is `violation`, `match`, `mismatch`, `addition` or `unverified`. Required `title` states the concrete finding; `specified` and `choice` quote short, exact, unique, non-overlapping fragments from those fields, and `note` explains the evidence-backed comparison. A match needs both sides; an addition marks only the actual choice; mismatch/unverified may mark one side when its counterpart is absent. Optional `impact` is a source cell for this finding's effects; otherwise the expanded explanation labels the row's effects as applying to the whole item. The template preserves full text, colors, paired numbers and explanations, and rejects missing titles or stale/ambiguous fragments. Addition marks contribute to the outer unspecified marker; mismatch or unverified implementation does not change specification status.

`violation` also requires both fragments and `constraint_source` naming the applicable user restriction's source. It appears first, with a prominent finding headline, requirement/behavior comparison, red text marks and graph badges propagated to ancestors. Effects and evidence expand on demand. Supply the evidence-backed classification; the renderer does not infer a violation from keywords or missing instructions.

Summary and node details share the finding renderer: violations/mismatches show a headline and two-column comparison, added choices show compact expandable titles, and unreviewed specification and unverified implementation remain separate. Narrow layouts stack the comparison. Node details retain purpose, full marked wording, sources, diagrams and the original three fields under “完整原文、来源与取舍”. Existing generated files are unchanged; rebuilding older report input requires adding comparison titles.

| State input | Meaning |
| --- | --- |
| `specification='specified'` | Explicitly specified within this item's scope. |
| `specification='unspecified'` | Source-checked choice the user did not specify; remains after the Agent chooses an implementation. |
| `specification='unreviewed'` | Specification not investigated; default when evidence is absent. |
| `pending=True` | A design decision remains unresolved, independently of specification. |

Specification describes what the user has specified; unverified implementation belongs in `choice` as **未核实**. `specified.missing` may name a verified partial gap; count only identified choices, with unchecked scope separate. The builder retains both unspecified and unreviewed markers when they coexist, including detail-diagram and descendant states; pending remains independent. Summary groups distinguish a locally unresolved decision (方案待定) from pending mini items (含待定方案); only the affected mini findings carry their own pending badge. Items with no other finding still appear as pending-only entries. Parent markers do not imply that every child has the same state or that implementation passed.

For a meaningful small relationship, add `diagram={label, lanes, nodes, edges}` to a `specified` or `choice` cell; retain complete text and source in that cell.

| Detail-diagram input | Fields |
| --- | --- |
| `lanes` | Rows of local node keys, each once; `None` leaves a space. |
| Node | `label`, full `detail` source cell, optional `specification`/`pending`, finding `title` and `impact`. |
| Edge | `from`, `to`, optional `label`, `detail`, `specification`/`pending`, finding `title`/`impact`, `kind='constraint'` for association. |

Use a few short nodes (usually 2–5); `specification='context'` is available only here for neutral material/result labels. These selectable explanations are terminal details, not another expansion level.

## Use The Generated Viewer

The viewer starts with the root, expands one selected branch per depth below its ancestors, and provides parent context, terminal details, deep links, zoom/scroll/drag, keyboard controls and per-view session position; styling and complete HTML/standalone-SVG legends come from the template.

`summary.html` groups `violation` first, then `mismatch`, `addition`, unreviewed specification, `unverified` implementation and pending-only entries; `match` is omitted. The unreviewed and pending-only sections appear only when populated; their generated finding kinds do not extend the authored `comparisons` kinds. Missing actual text, local unspecified/unreviewed states, and each marked detail-diagram node/relation remain visible independently of prose annotations. Descendant rollups are not counted again; counts describe entries, not unique defects. Register every prose/Markdown finding in the relevant comparisons or marked detail items and reconcile them before delivery: free-form Markdown is not automatically interpreted as findings.

Summary links use `index.html#inspect-view--node` to open that item's own detail directly, even when it has a child view, with a return link. Ordinary `#view--node` links keep the diagram/expansion behavior.

Selection replaces content in place; newly revealed content scrolls gently into view only when needed. Precise links reveal their target inside the canvas without resetting zoom.

Printing exposes all views, full-report details and sources, then restores the reading state. The full-report entry retains every branch, source and appendix; include the complete check content in `source_html` when delivering a semantic check.

Presets handle geometry; use local view `positions` or edge/handoff `route` overrides only when needed, following [flow.py](../assets/audit-svg/flow.py).

## Verify And Deliver

Output is self-contained `index.html`, `summary.html` and one SVG per view; keep the two HTML pages together for their cross-links, preserve builder dependencies when rebuilding is part of delivery, and follow [semantic-check delivery](audit-presentation.md#report-contract-markdown-and-visual-html) for the Markdown source.

The entry checks the generated report's structure, links between summary and diagram, details and basic geometry; verify the actual content, handoffs and evidence independently.

When permitted, inspect normal/narrow browser layouts, labels, node/relation/detail selection, keyboard controls, source access, scrolling and zoom; state what remains unverified, since automated checks do not prove browser layout or semantic completeness.
