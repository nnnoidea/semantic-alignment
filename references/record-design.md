# Record Design

This reference explains the document structure. It does not prescribe which reading tools to use or a reading sequence.

## One Project Design, Multiple Reading Units

For a short design, SEMANTICS.md can contain all topics. A long design can use an entry point plus cohesive topic documents. A workflow platform might have topics such as:

```text
SEMANTICS.md
semantics/
  task-execution.md        task construction, readiness, records, Run completion
  agent-lifecycle.md       scope, ownership, concurrency, finish, stop, retry
  agent-integration.md     commands, platform Skill, author/node Skills, sessions
  collaboration.md         named agents, groups, requests, NAS transport
  notifications.md         routing, chat origin, Bots, receipts, fallback
  editor.md                graph meaning, drafts, save, navigation
  sharing.md               Loop packages, binding, installation readiness
  host-runtime.md          platform service, operating systems, power protection
```

These are illustrative topic boundaries, not an imposed eight-file template. Reorganize according to the actual project, keeping a behavioral chain together. Repeated statements may merge; a compound statement may contribute to multiple topics, each with a distinct responsibility.

SEMANTICS.md keeps only shared design and navigation. Each topic link explains what that document owns; it is not an abridged copy of its requirements. A scope description like "notification destination, original chat thread, Bot fallback and delivery receipts" lets an agent choose a document without opening all documents or maintaining a keyword database.

Promote a topic to a separate document when it has a distinct change boundary and substantial content. Do not split a complete operation merely because a byte or line limit was reached. If large files remain, use meaningful subheadings. A document growing to several thousand words is a reason to inspect its boundaries, not an automatic splitting threshold.

## Why This Fits Common File Tools

| Tool capability | Structural consequence |
| --- | --- |
| Listing files and matching paths | Descriptive topic filenames distinguish responsibilities before loading text; a conventional entry point makes ownership discoverable. |
| Searching text and returning nearby lines | Product terms belong in titles and prose; important restrictions live beside the behavior they qualify. |
| Reading a whole file or a line range | Topic documents are coherent units; subheadings form useful smaller boundaries without requiring an artificial semantic ID. |
| Applying a local textual patch | Current prose has one authoritative home and ordinary physical line/paragraph breaks; changing one meaning need not rewrite a giant paragraph or several copies. |

No persistent line-number index, generated table of contents, duplicated summary, machine registry, or custom reader is needed. The short topic directory is ordinary authored navigation maintained only when document boundaries change.

This structure reduces irrelevant loaded text. It does not guarantee an exact token reduction or complete semantic recall; vocabulary mismatches and broad shared control points still require judgment. Do not claim savings by counting discarded restrictions as compression.

## Local Completeness Without A Relation Graph

A topic supplies its applicable scope, important conditions, and exceptions in the same narrative. Shared constraints have a single home in SEMANTICS.md. A concrete dependency is expressed near the dependent behavior with a normal link and a description of what matters.

For example, notification routing can explain Bot selection locally but link to collaboration for request ownership. It should not repeat all transport and execution rules or list every remotely related topic. Identity, natural-language authorization, and operation ownership must remain distinct even when spread across topic boundaries.

Use separate paragraphs for independently changeable aspects of a topic, and useful subheadings for larger aspects. Normal lists remain available for parallel rules. There is no mandatory paragraph schema or one-rule-per-heading requirement. Avoid an entire topic squeezed onto one physical line: it makes search output noisy and patches unnecessarily large.

## Migration

Use the latest accepted design as the source, not the full event ledger. Review current known gaps and active alternatives separately. Consolidate repetitions and remove obsolete phase-specific narration only when their meaning is demonstrably superseded; unfamiliar terminology alone is not proof that a requirement is obsolete.

Check that every distinct condition, prohibition, exception, and acceptance boundary survives reorganization. A temporary migration checklist can help, but does not become a replacement per-semantic database. Only investigate historical material to resolve a specific ambiguity.

After adoption, old generators must no longer overwrite the new canonical prose. Removing old records is a separate migration action within the user's actual authorization. Old coverage labels are not fresh implementation evidence. Without standing snapshots, checks report their actual scope rather than claiming automatic freshness since a previous audit.
