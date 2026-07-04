# Semantic Alignment

[English README](README.md)

AI agent 最大的问题，不是不会做事，而是会悄悄把事情做成另一个东西。

用户说的是目标。agent 落地时会补细节、绕限制、改路线。一次两次看不出来，项目推进久了，最初为什么这样做、哪些是用户要的、哪些是 agent 自己加的、哪些只是临时妥协，就会混在一起。

`semantic-alignment` 让这些漂移保持可见。

它让 agent 记住用户真正要什么，记录自己实现时补了什么、改了什么、为什么，并在审计时逐条对账。用户也应在关键节点主动发起审计，及时校准语义，避免项目在推进中悄悄偏离。

一句话：它让 agent 不只是完成任务，而是持续证明自己做出来的东西，仍然是用户想要的那个东西。

## 它怎么解决

这个 skill 会把项目语义拆成几类稳定记录：

- `user-semantics.md`：用户当前真正想要什么
- `user-semantic-ledger.md`：语义从什么变成什么，以及为什么变
- `recheck-triggers.md`：什么可观察条件出现时，旧决定需要重新检查
- `realization-semantics.md`：agent 理解用户后，打算在产物中实现什么
- `artifact-checks.md`：真实代码、设计或文档是否符合这些实现语义
- `audits.md`：跨这些层的对齐判断

关键点是：用户语义、agent 补出来的实现语义、真实产物，不会被混成一件事。

## 它审计什么

审计时，这个 skill 会推动 agent 回答具体问题，而不是写一段笼统总结：

- 哪些用户语义已经满足、部分满足、未满足、未知或冲突？
- 哪些实现细节是用户直接要求的？
- 哪些细节是 agent 补充的，但仍然服务于用户语义？
- 哪些补充有风险，或已经和用户语义冲突？
- 真实产物是否符合 agent 以为自己实现的语义？
- 旧限制是否已经消失，导致过去的临时妥协需要调整？

例如，当初因为无法导出文件，所以采用复制到剪贴板；如果现在文件导出可用了，trigger 应提醒 agent 重新检查旧路线。agent 如果增加了自动保存、快捷键、导航结构或公开文案，审计时也应该判断这些补充是合理细节，还是语义漂移。

## Trigger 怎么工作

recheck trigger 不是任务，也不是建议。它是一个可观察条件，意思是：“重新读取对应的 ledger 记录，判断旧语义决定是否还成立。”

agent 会在加载语义框架时读取紧凑的 trigger 投影；在重要规划或交付前、用户提到限制条件变化时、真实产物暴露新证据时、以及审计时，也要对照 trigger。若某个 trigger 看起来已经成真，agent 必须读取对应 ledger，说明旧路线和当前成真的条件，并在继续旧路线或修改基线前，把这个提醒明确告诉用户。

## 工作方式

在重要任务开始前，agent 会先读取当前语义框架，再进行规划或修改。

这个 skill 将对齐检查分成三层：

1. **用户语义**：用户当前想要什么。
2. **实现语义**：agent 理解用户后，打算在产物中实现什么。
3. **产物检查**：真实代码、设计、文档或输出是否符合这些实现语义。

当语义发生重要变化时，agent 会记录这是新增、更新还是删除，并记录原因。如果变化由限制条件导致，还可以留下后续重新检查的 trigger。

完整审计由用户发起或确认。审计前，agent 应先检查真实项目，刷新或确认实现语义，再刷新或确认产物检查。完整审计应覆盖每条当前用户语义和每条 active 实现语义。

## 安装

将本仓库作为名为 `semantic-alignment` 的 skill 安装到 Codex 或兼容的 agent 环境中。

skill 根目录结构：

```text
semantic-alignment/
  SKILL.md
  references/
  scripts/
  agents/
```

安装后，在需要长期保持意图一致的项目、设计、实现或写作任务中，让 agent 使用 `semantic-alignment`。

## 记录放在哪里

默认记录目录：

```text
.semantic-alignment/<project-slug>/
```

这个目录可以放在项目根目录，也可以放在 workspace 根目录。若一个 workspace 中有多个 project，每个 project 应使用独立的 slug。project slug 是稳定的小写 kebab-case 项目标识，通常来自仓库根目录名、包/项目名或项目目录名。

主要文件包括：

- `user-semantics.md`：给用户查看的当前语义基线
- `user-semantic-ledger.md`：已接受的语义变化和原因
- `recheck-triggers.md`：需要重新检查旧决定的条件
- `realization-semantics.md`：agent 打算实现到产物中的语义
- `artifact-checks.md`：真实产物和实现语义之间的检查
- `audits.md`：对齐、漂移、冲突和建议

这些记录属于项目过程元数据，不是产品本身。

## 示例

`examples/semantic-alignment-skill/` 包含这个 skill 在开发过程中的语义记录。

这些文件仅作为示例，用来展示真实项目中语义记录如何演化。安装或运行 skill 不依赖它们。

## 当前状态

这个 skill 目前按 Codex skill 的形式打包，但记录模型本身尽量保持平台无关。
