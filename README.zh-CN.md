# Semantic Alignment

[English README](README.md)

AI Agent 最常见的问题不是不会实现，而是实现结果在不知不觉中偏离了用户真正想要的东西。

`semantic-alignment` 保存完整的用户设计语义，用真实代码或产物反推出当前实现语义，再把两者的差异直接呈现给用户。用户不需要日常阅读全部内部记录，只需要判断这些差异是否合理。

它只管理长期存续的产品和系统设计。一次性实验、研究运行状态、临时分析和普通写作默认不创建语义记录；只有用户明确要求，或产物本身是约束后续实现的权威规范时才纳入。实验结论被用户接受为长期决策后，只把该决策写入所属产品项目，不把实验本身登记成语义项目。

## 核心设计

新版工作流只长期维护两类无法从代码可靠恢复的信息：

- 用户设计语义：目标、原则、全局与局部设计、约束和验收标准。
- 妥协：原目标、实际方案、差距、原因、证据和重审条件。

只要用户明确表达或接受了会长期约束产品/系统实现的语义，即使改动很小、风险很低，也必须持久化。不存在“只留在对话”的轻量模式；轻量化来自复用增量审计结果，而不是省略语义记录。

实现语义不再要求 Agent 边开发边维护一份手写副本，而是在审计时从真实产物中提取。

审计结果按以下条件缓存：

```text
用户语义修订版 + 直接相关语义及版本 + 证据范围与文件状态版本 + 已审查的产物快照
```

每条语义可以维护一个简单、无类型、只展开一层的 `related` 集合。审计以单条用户语义为入口，同时查看直接相关的少量语义。只要这些条件没有变化，旧结论就可以复用；无关语义的变化不会使其失效。

每审完一条语义及其直接相关上下文，Agent 立即调用工具保存结论，不等待整个审计结束。这样即使任务中断或上下文被压缩，也能从持久化状态继续。

对于“必须”或“不得”类语义，审计还必须检查路由、模式、例外、fallback 和提前退出。主路径能够工作只能证明具备能力，不能证明所有适用路径都遵守用户语义。

## 用户会看到什么

默认报告只展示有判断价值的内容：

- Agent 新增或增强了什么；
- 哪些用户要求被遗漏、替换、收窄或冲突；
- 实际产物是否发生漂移；
- 哪些历史妥协现在可能需要重新考虑。

例如，用户没有要求测试、重试或校验，而实现中增加了这些行为，它们即使合理，也会作为差异显示。

## 记录结构

每个项目在自身目录内保存唯一权威记录：

```text
<project-root>/.semantic-alignment/
  project.json
  user-semantics.md
  semantic-ledger.jsonl
  compromises.jsonl
  audit-state.json
  alignment-report.md
```

- `project.json`：稳定项目 ID 和项目内记录布局。
- `user-semantics.md`：完整、当前、可供用户阅读的设计语义。
- `semantic-ledger.jsonl`：具有稳定 ID 和修订号的用户语义历史。
- `compromises.jsonl`：独立保存的妥协及重审条件。
- `audit-state.json`：实现语义、低成本证据版本、覆盖状态和产物快照。
- `alignment-report.md`：面向用户的当前差异与妥协摘要。

用户语义、妥协和审计结论都必须通过脚本记录。两个 Markdown 文件由脚本生成，Agent 不直接手写 JSONL、审计状态或生成视图。

多项目 Workspace 只额外保存一份路由索引：

```text
<workspace-root>/.semantic-alignment/projects.json
```

索引只包含稳定项目 ID 和相对路径，由项目内 `project.json` 重建，不复制语义、妥协、差异或审计覆盖。`related` 只能关联同一项目内的语义；真正跨项目的共同语义应归属于单独注册的共同上层项目。

## 增量审计

```bash
python semantic-alignment/scripts/audit.py <record-dir> plan --artifact-root <project-root>
```

该命令会列出：

- 新增、修改和删除的产物文件；
- 尚未覆盖的用户语义；
- 因用户语义或证据变化而失效的旧结论；
- 每个待审计语义的直接相关语义；
- 证据已经变化的实现差异；
- 建议使用增量审计还是完整审计。

Agent 对着待审计用户语义检查真实产物，并在每个小组完成后立即记录覆盖结论；全部必要语义和变化产物处理完后，再提交新的可信快照。

## 妥协提醒

妥协不能依赖代码审计恢复，因为相同代码可能来自完全不同的原因。因此妥协在决策发生时记录，并只在以下情况提醒：

- 当前工作涉及它影响的语义或范围；
- 新证据符合其重审条件；
- 相关工具、权限、依赖、资源或约束发生变化。

## 初始化与迁移

初始化并注册项目内记录：

```bash
python semantic-alignment/scripts/workspace.py init <project-root> \
  --workspace-root <workspace-root> --project-id <stable-project-id>
```

列出、定位、检查或重建 Workspace 索引：

```bash
python semantic-alignment/scripts/workspace.py list --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py resolve <artifact-path> --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py check --workspace-root <workspace-root> --discover
python semantic-alignment/scripts/workspace.py archive-project <project-id> --workspace-root <workspace-root>
python semantic-alignment/scripts/workspace.py rebuild-index --workspace-root <workspace-root>
```

默认 `check` 只验证已保存索引，不重新扫描 Workspace；只有需要查找未登记项目记录时才使用 `--discover`。

旧的 Workspace 集中记录或同一项目下的多套旧记录，可使用 `scripts/migrate_v1.py <旧记录目录> --into <项目根>/.semantic-alignment --source-label <标签>` 合并到项目本地记录。先预览，再添加 `--apply`；已经确认由 canonical 记录取代的旧镜像可用 `--archive-only` 仅归档。

旧版记录先预览迁移：

```bash
python semantic-alignment/scripts/migrate_v1.py <record-dir>
```

确认后执行：

```bash
python semantic-alignment/scripts/migrate_v1.py <record-dir> --apply
```

旧文件会被保存在 `archive/legacy-v1-*`。旧审计因为缺少完整证据范围和文件状态版本，不会被冒充成可复用的新审计缓存；迁移后只有在用户发起或接受的前提下，才能执行一次基线完整审计并据此宣称对齐。

## 安装

将本仓库安装为名为 `semantic-alignment` 的 Codex 或兼容 Agent Skill。记录模型本身不依赖特定 Agent 平台。
