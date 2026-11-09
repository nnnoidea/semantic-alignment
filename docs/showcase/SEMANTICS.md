# Semantic Alignment

## 目的

以用户当前有效的语义为依据开展语义检查，帮助用户发现 Agent 在实现过程中是否自作主张：要求是否兑现、哪些细节由 Agent 自行补足。可视化是检查结果的输出方式。

## 限制

语义记录只保存用户表达或已接受的含义。“最终期望”和“当前阶段约定”都是用户语义，不是真实实现或完成状态；检查须另查产物。用户明确留到后续的能力仍保留，但不判成本阶段遗漏。

用户原话：“在记录语义文件时，需要尽可能用用户原话，在可视化时也是，如果太长的话则稍微压缩，这样便于用户理解”。

使用 Markdown 正文，按用户关心的对象或能力分组；不建立逐条语义对象、JSON 账本、开发历史、常驻覆盖缓存或长期备选方案库。未知约定写“未约定”，不替用户补目标、阶段安排和完成条件。

本项目的语义记录和维护资料保留在 Skill 安装包之外；未进入安装包不构成删除理由。仅维护英文正式 Skill。

以下主题分组，以及各主题的关联约定和关联文件，均为 Agent 按当前约定整理的导航索引；分组和文件拆分不自动定义实现模块。文件存在和路径关联不证明已实现，也不自动成为用户限定的实现路径。

## 用户约定

以下按主题索引约定正文；共同限制适用于相关主题，具体约定见链接。

### [触发与任务范围](semantics/activation.md)

- [长期语义维护](semantics/activation.md#长期语义维护)
- [语义检查入口](semantics/activation.md#语义检查入口)

### [语义记录](semantics/records.md)

- [记录结构与文件组织](semantics/records.md#记录结构与文件组织)
- [当前含义更新](semantics/records.md#当前含义更新)
- [记录迁移](semantics/records.md#记录迁移)

### [语义检查](semantics/audit.md)

- [要求与产物双向对照](semantics/audit.md#要求与产物双向对照)
- [全部选择披露](semantics/audit.md#全部选择披露)
- [可省附加机制](semantics/audit.md#可省附加机制)
- [修复确认](semantics/audit.md#修复确认)
- [结果呈现与交付](semantics/audit.md#结果呈现与交付)

### [Skill 说明与交付](semantics/packaging.md)

- [说明与版本](semantics/packaging.md#说明与版本)
